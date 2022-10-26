import textwrap
import typing as t

import markdown
from markupsafe import Markup
from markdown.extensions.toc import slugify_unicode  # type: ignore
from tcom.catalog import Catalog

from .utils import current_path, is_current_path, load_markdown_metadata, logger

if t.TYPE_CHECKING:
    from .utils import THasPaths


DEFAULT_MD_EXTENSIONS = [
    "attr_list",
    "meta",
    "sane_lists",
    "smarty",
    "tables",
    "toc",
    "pymdownx.betterem",
    "pymdownx.caret",
    "pymdownx.critic",
    "pymdownx.emoji",
    "pymdownx.highlight",
    "pymdownx.inlinehilite",
    "pymdownx.keys",
    "pymdownx.magiclink",
    "pymdownx.mark",
    "pymdownx.saneheaders",
    "pymdownx.smartsymbols",
    "pymdownx.superfences",
    "pymdownx.tasklist",
    "pymdownx.tilde",
]

DEFAULT_MD_EXT_CONFIG = {
    "keys": {
        "camel_case": True,
    },
    "toc": {
        "marker": "",
        "toc_class": "",
        "anchorlink": False,
        "permalink": True,
        "slugify": slugify_unicode,
    },
    "pymdownx.highlight": {
        "linenums_style": "pymdownx-inline",
        "anchor_linenums": True,
    },
}


class DocsRender(THasPaths if t.TYPE_CHECKING else object):
    def __init__(
        self,
        *,
        globals: "t.Optional[dict[str,t.Any]]" = None,
        filters: "t.Optional[dict[str,t.Any]]" = None,
        tests: "t.Optional[dict[str,t.Any]]" = None,
        extensions: "t.Optional[list]" = None,
        md_extensions: "t.Optional[list[str]]" = None,
        md_ext_config: "t.Optional[dict[str,t.Any]]" = None,
    ) -> None:
        self.markdowner = markdown.Markdown(
            extensions=md_extensions or DEFAULT_MD_EXTENSIONS,
            extension_configs=md_ext_config or DEFAULT_MD_EXT_CONFIG,
            output_format="html",
            tab_length=2,
        )

        globals = globals or {}
        globals.setdefault("current_path", current_path)
        filters = filters or {}
        filters.setdefault("current_path", current_path)
        tests = tests or {}
        tests.setdefault("current_path", is_current_path)
        extensions = extensions or []
        extensions += ["jinja2.ext.loopcontrols"]

        catalog = Catalog(
            globals=globals,
            filters=filters,
            tests=tests,
            extensions=extensions,
        )
        catalog.add_folder(self.content_folder)
        catalog.add_folder(self.components_folder)
        catalog.add_folder(self.theme_folder)
        self.catalog = catalog

    def render(self, name: str, **kw) -> str:
        filename = f"{name}.md"
        logger.debug(f"Trying to render `{name}`...")
        filepath = self.content_folder / filename
        logger.debug(f"Looking for `{filepath}`...")
        if not filepath.exists():
            filename = f"{name}/index.md"
            filepath = self.content_folder / filename
            logger.debug(f"Looking for `{filepath}`...")
            if not filepath.exists():
                return ""

        logger.debug(f"Rendering `{filepath}`")
        md_source, meta = load_markdown_metadata(filepath)
        meta.update(kw)
        page = self.nav.get_page(filename)
        meta.setdefault("component", self.DEFAULT_COMPONENT)
        meta.setdefault("title", page["title"])
        meta.setdefault("section", page["section"])

        component = meta["component"]
        content = self.render_markdown(md_source)
        source = "<%(component)s __attrs={attrs}>%(content)s</%(component)s>" % {
            "component": component,
            "content": content,
        }

        page_toc = self.nav.get_page_toc(self.markdowner.toc_tokens)  # type: ignore
        self.catalog.jinja_env.globals["nav"] = {
            "page": page,
            "page_toc": page_toc,
            "prev_page": self.nav.get_prev(url=page["url"]),
            "next_page": self.nav.get_next(url=page["url"]),
            "toc": self.nav.toc,
        }
        return self.catalog.render(component, source=source, **meta)

    def render_markdown(self, source: str) -> Markup:
        source = textwrap.dedent(source.strip("\n"))
        html = (
            self.markdowner.convert(source)
            .replace("<code", "{% raw %}<code")
            .replace("</code>", "</code>{% endraw %}")
        )
        return Markup(html)

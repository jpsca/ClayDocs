import os
import textwrap
import typing as t
from hashlib import md5

from image_processing import ImageProcessing
import inflection
import markdown
from pymdownx import emoji
from markupsafe import Markup
from markdown.extensions.toc import slugify_unicode  # type: ignore
from tcom.catalog import Catalog

from .utils import load_markdown_metadata, logger

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
    "pymdownx.emoji",
    "pymdownx.highlight",
    "pymdownx.inlinehilite",
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
        "linenums": True,
        "linenums_style": "pymdownx-inline",
        "anchor_linenums": True,
        "css_class": "highlight not-prose",
    },
    "pymdownx.emoji": {
        "emoji_generator": emoji.to_alt,
    },
}

UTILS = {
    "camelize": inflection.camelize,
    "humanize": inflection.humanize,
    "ordinal": inflection.ordinal,
    "ordinalize": inflection.ordinalize,
    "parameterize": inflection.parameterize,
    "pluralize": inflection.pluralize,
    "singularize": inflection.singularize,
    "titleize": inflection.titleize,
    "underscore": inflection.underscore,
}
DEFAULT_EXTENSIONS = [
    "jinja2.ext.loopcontrols",
]


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
        self.__init_thumbnailer__()
        self.__init_catalog__(globals, filters, tests, extensions)

    def __init_thumbnailer__(self) -> None:
        this = self

        class Thumbnailer(ImageProcessing):
            def __init__(self, source: str) -> None:
                super().__init__(this.static_folder / source)

            def __str__(self) -> str:
                ops = str(self.options).encode("utf8", errors="ignore")
                filename = md5(ops).hexdigest()
                dest = this.temp_folder / filename
                self.save(dest)
                return f"/{self.THUMBNAILS_URL}/{filename}"

        self.Thumbnailer = Thumbnailer

    def __init_catalog__(
        self,
        globals: "t.Optional[dict[str,t.Any]]" = None,
        filters: "t.Optional[dict[str,t.Any]]" = None,
        tests: "t.Optional[dict[str,t.Any]]" = None,
        extensions: "t.Optional[list]" = None,
    ) -> None:
        _globals = globals or {}
        _globals["utils"] = UTILS.copy()
        _globals["utils"]["thumb"] = self.Thumbnailer

        _filters = filters or {}
        _filters["utils"] = UTILS.copy()

        _tests = tests or {}

        _extensions = extensions or []
        _extensions += DEFAULT_EXTENSIONS

        catalog = Catalog(
            globals=_globals,
            filters=_filters,
            tests=_tests,
            extensions=_extensions,
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

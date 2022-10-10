import random
import sys
import textwrap
from pathlib import Path
from signal import SIGTERM, signal
import typing as t

import markdown
from markdown.extensions.toc import slugify_unicode  # type: ignore
from markupsafe import Markup
from tcom.catalog import Catalog

from .docs_builder import DocsBuilder
from .docs_server import DocsServer
from .nav import Nav
from .utils import load_markdown_metadata, logger

if t.TYPE_CHECKING:
    from .nav import TNavConfig


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

RANDOM_MESSAGES = [
    "Distilling enjoyment",
    "Adding emotional depth",
    "Filtering the ozone",
    "Testing for perfection",
    "Stretching the truth",
    "Optimizing for happiness",
    "Swapping time and space",
    "Reversing the polarity",
    "Self-affirming",
    "Extracting meaning",
]


class Markdown(markdown.Markdown):
    pass


class Docs(DocsServer, DocsBuilder):
    COMPONENTS_FOLDER = "components"
    CONTENT_FOLDER = "content"
    STATIC_FOLDER = "static"
    BUILD_FOLDER = "build"
    STATIC_URL = "static"
    DEFAULT_COMPONENT = "Page"

    def __init__(
        self,
        nav_config: "TNavConfig",
        *,
        root: "t.Union[str,Path]" = ".",
        globals: "t.Optional[dict[str,t.Any]]" = None,
        filters: "t.Optional[dict[str,t.Any]]" = None,
        tests: "t.Optional[dict[str,t.Any]]" = None,
        extensions: "t.Optional[list]" = None,
        md_extensions: "list[str]" = DEFAULT_MD_EXTENSIONS,
        md_ext_config: "dict[str,t.Any]" = DEFAULT_MD_EXT_CONFIG,
    ) -> None:
        root = Path(root)
        if root.is_file():
            root = root.parent
        self.root = root
        self.components_folder = root / self.COMPONENTS_FOLDER
        self.content_folder = root / self.CONTENT_FOLDER
        self.static_folder = root / self.STATIC_FOLDER
        self.build_folder = root / self.BUILD_FOLDER

        self.nav = Nav(self.content_folder, nav_config)
        self.markdowner = Markdown(
            extensions=md_extensions,
            extension_configs=md_ext_config,
            output_format="html",
            tab_length=2,
        )
        self.init_catalog(
            globals=globals,
            filters=filters,
            tests=tests,
            extensions=extensions,
        )
        super().__init__()

    def init_catalog(
        self,
        globals: "t.Optional[dict[str,t.Any]]" = None,
        filters: "t.Optional[dict[str,t.Any]]" = None,
        tests: "t.Optional[dict[str,t.Any]]" = None,
        extensions: "t.Optional[list]" = None,
    ) -> None:
        globals = globals or {}
        filters = filters or {}
        tests = tests or {}
        extensions = extensions or []

        catalog = Catalog(
            globals=globals,
            filters=filters,
            tests=tests,
            extensions=extensions,
        )
        catalog.add_folder(self.components_folder)
        catalog.add_folder(self.content_folder)
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
        meta["nav"] = {
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

    def print_random_messages(self, num=2) -> None:
        for message in random.sample(RANDOM_MESSAGES, num):
            logger.info(f"{message}...")

    def run(self) -> None:
        def sigterm_handler(_, __):
            raise SystemExit(1)

        signal(SIGTERM, sigterm_handler)

        try:
            py, *sysargs = sys.argv
            cmd = sysargs[0] if sysargs else "serve"
            if cmd == "serve":
                self.serve()
            elif cmd == "build":
                self.build()
            else:
                print(
                    f"""
Valid commands:
  python {py} serve
  python {py} build
"""
                )
        finally:
            sys.stderr.write("\n")
            exit(1)

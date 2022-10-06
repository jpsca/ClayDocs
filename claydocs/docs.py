import textwrap
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

import markdown
import pymdownx
from markupsafe import Markup
from tcom import Catalog

from .utils import current_path, highlight, load_markdown_metadata
from .nav_tree import NavTree
from .wsgi import WSGIApp

if TYPE_CHECKING:
    from .nav_tree import TNavConfig


COMPONENTS_FOLDER = "components"
CONTENT_FOLDER = "content"
STATIC_FOLDER = "static"
STATIC_URL = "static"
DEFAULT_COMPONENT = "Page"
DEFAULT_MD_EXTENSIONS = [
    "attr_list",
    "sane_lists",
    "smarty",
    "tables",
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
    "pymdownx.highlight": {
        "linenums_style": "pymdownx-inline",
        "anchor_linenums": True,
    },
    "keys": {
        "camel_case": True,
    },
}


class Markdown(markdown.Markdown):
    pass


class Docs:
    def __init__(
        self,
        nav_config: "TNavConfig",
        *,
        root: str = ".",
        globals: "Optional[dict[str, Any]]" = None,
        filters: "Optional[dict[str, Any]]" = None,
        tests: "Optional[dict[str, Any]]" = None,
        extensions: "Optional[list]" = None,
        md_extensions: "list[str]" = DEFAULT_MD_EXTENSIONS,
        md_ext_config: "dict[str, Any]" = DEFAULT_MD_EXT_CONFIG,
    ) -> None:
        root = Path(root)
        if root.is_file():
            root = root.parent
        self.components_folder = root / COMPONENTS_FOLDER
        self.content_folder = root / CONTENT_FOLDER

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
        self.init_app(root)
        self.nav = NavTree(self.content_folder, nav_config)

    def init_catalog(
        self,
        globals: "Optional[dict[str, Any]]" = None,
        filters: "Optional[dict[str, Any]]" = None,
        tests: "Optional[dict[str, Any]]" = None,
        extensions: "Optional[list]" = None,
    ) -> None:
        globals = globals or {}
        globals.setdefault("current_path", current_path)
        globals.setdefault("highlight", highlight)
        globals.setdefault("markdown", self.markdowner)
        filters = filters or {}
        filters.setdefault("current_path", current_path)
        filters.setdefault("highlight", highlight)
        filters.setdefault("markdown", self.markdowner)
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

    def init_app(self, root: str) -> None:
        app = WSGIApp(self)
        middleware = self.catalog.get_middleware(
            app.wsgi_app,
            allowed_ext=None,  # All file extensions allowed as static files
            autorefresh=True,
        )
        middleware.add_files(root / STATIC_FOLDER, STATIC_URL)
        app.wsgi_app = middleware
        self.app = app

    def render(self, name: str, **kw) -> str:
        name = f"{name}.md"
        filepath = self.content_folder / name
        if not filepath.exists():
            return ""

        md_source = filepath.read_text()
        meta, md_source = load_markdown_metadata(md_source, name)
        kw.update(meta)
        component = meta.get("component", DEFAULT_COMPONENT)
        source = self.render_markdown(md_source)
        source = f"<{component}>{source}</{component}>"
        return self.catalog.render(name, source=source, **kw)

    def render_markdown(self, source: str):
        source = textwrap.dedent(source.strip("\n"))
        html = (
            self.markdowner.convert(source)
            .replace("<code", "{% raw %}<code")
            .replace("</code>", "</code>{% endraw %}")
        )
        return Markup(html)

    def serve(self) -> None:
        self.app.run()

    def build(self) -> None:
        pass

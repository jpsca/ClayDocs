import textwrap
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Optional
from xmlrpc.server import resolve_dotted_attribute

import jinja2
import markdown
from markupsafe import Markup
from tcom import Catalog

from .exceptions import Abort
from .nav_tree import NavTree
from .utils import current_path, highlight, load_markdown_metadata, logger
from .wsgi import LiveReloadServer

if TYPE_CHECKING:
    from .nav_tree import TNavConfig


COMPONENTS_FOLDER = "components"
CONTENT_FOLDER = "content"
STATIC_FOLDER = "static"
STATIC_URL = "static"
DEFAULT_COMPONENT = "Page"
DEFAULT_MD_EXTENSIONS = [
    "attr_list",
    "meta",
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
        self.root = resolve_dotted_attribute
        self.components_folder = root / COMPONENTS_FOLDER
        self.content_folder = root / CONTENT_FOLDER
        self.static_folder = root / STATIC_FOLDER

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
        globals.setdefault("markdown", self.render_markdown)
        filters = filters or {}
        filters.setdefault("current_path", current_path)
        filters.setdefault("highlight", highlight)
        filters.setdefault("markdown", self.render_markdown)
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
        name = f"{name}.md"
        filepath = self.content_folder / name
        if not filepath.exists():
            return ""

        source, meta = load_markdown_metadata(filepath)
        content = self.render_markdown(source)
        component = meta.pop("component", DEFAULT_COMPONENT)
        kw.update(meta)
        return self.catalog.render(component, content=content, **kw)

    def render_markdown(self, source: str):
        source = textwrap.dedent(source.strip("\n"))
        html = (
            self.markdowner.convert(source)
            .replace("<code", "{% raw %}<code")
            .replace("</code>", "</code>{% endraw %}")
        )
        return Markup(html)

    def serve(self) -> None:
        try:
            server = self._get_server()
            server.watch(self.components_folder)
            server.watch(self.content_folder)
            server.watch(self.static_folder)

            try:
                server.serve()
            except KeyboardInterrupt:
                print()  # To clear the printed ^C
            finally:
                server.shutdown()
        except jinja2.exceptions.TemplateError:
            # This is a subclass of OSError, but shouldn't be suppressed.
            raise
        except OSError as err:  # pragma: no cover
            # Avoid ugly, unhelpful traceback
            raise Abort(f"{type(err).__name__}: {err}")

    def build(self) -> None:
        logger.info("Building docs...")
        for url, data in self.nav.titles.items():
            pass
        logger.info("Done!")


    def _get_server(self) -> LiveReloadServer:
        server = LiveReloadServer(render=self.render)

        middleware = self.catalog.get_middleware(
            server.application,
            allowed_ext=None,  # All file extensions allowed as static files
            autorefresh=True,
        )
        middleware.add_files(self.static_folder, STATIC_URL)
        server.application = middleware
        return server

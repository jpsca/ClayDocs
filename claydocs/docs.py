from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

from tcom import Catalog

from .ext_highlight import HighlightExtension
from .ext_markdown_render import MarkdownRenderExtension
from .ext_markdown_wrapper import MarkdownWrapperExtension
from .extra import current_path
from .nav_tree import NavTree
from .wsgi import WSGIApp

if TYPE_CHECKING:
    from .nav_tree import TNavConfig


COMPONENTS_FOLDER = "components"
CONTENT_FOLDER = "content"
STATIC_FOLDER = "static"
STATIC_URL = "static"


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
    ) -> None:
        root = Path(root)
        if root.is_file():
            root = root.parent

        self.init_catalog(
            root=root,
            globals=globals,
            filters=filters,
            tests=tests,
            extensions=extensions,
        )
        self.init_app(root)
        content_folder = root / CONTENT_FOLDER
        self.nav = NavTree(content_folder, nav_config)

    def init_catalog(
        self,
        root: str,
        globals: "Optional[dict[str, Any]]" = None,
        filters: "Optional[dict[str, Any]]" = None,
        tests: "Optional[dict[str, Any]]" = None,
        extensions: "Optional[list]" = None,
    ) -> None:
        components_folder = root / COMPONENTS_FOLDER
        content_folder = root / CONTENT_FOLDER

        globals = globals or {}
        globals.setdefault("current_path", current_path)
        filters = filters or {}
        filters.setdefault("current_path", current_path)
        tests = tests or {}
        extensions = extensions or []
        extensions = [
            MarkdownWrapperExtension,
            MarkdownRenderExtension,
            HighlightExtension,
        ] + extensions

        catalog = Catalog(
            globals=globals,
            filters=filters,
            tests=tests,
            extensions=extensions,
        )
        catalog.add_folder(components_folder)
        catalog.add_folder(content_folder)
        self.catalog - catalog

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
        kw["__file_ext"] = ".md"
        print("📋", f"{name}.md")
        return self.catalog.render(name, **kw)

    def serve(self) -> None:
        self.app.run()

    def build(self) -> None:
        pass

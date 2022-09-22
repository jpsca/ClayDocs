from pathlib import Path
from typing import Any, Optional

from tcom import Catalog

from .extra import current_path
from .highlight_extension import HighlightExtension
from .md_extension import MarkdownExtension
from .wsgi import WSGIApp


COMPONENTS_FOLDER = "components"
CONTENT_FOLDER = "content"
STATIC_FOLDER = "static"
STATIC_URL = "static"


class Docs:
    def __init__(
        self,
        root: str = ".",
        globals: "Optional[dict[str, Any]]" = None,
        filters: "Optional[dict[str, Any]]" = None,
        tests: "Optional[dict[str, Any]]" = None,
        extensions: "Optional[list]" = None,
    ) -> None:
        root = Path(root)
        if root.is_file():
            root = root.parent
        components_folder = root / COMPONENTS_FOLDER
        content_folder = root / CONTENT_FOLDER

        globals = globals or {}
        globals.setdefault("current_path", current_path)
        filters = filters or {}
        filters.setdefault("current_path", current_path)
        tests = tests or {}
        extensions = extensions or []
        extensions += [HighlightExtension, MarkdownExtension]

        catalog = Catalog(
            globals=globals,
            filters=filters,
            tests=tests,
            extensions=extensions,
        )
        catalog.add_folder(components_folder)
        catalog.add_folder(content_folder)

        app = WSGIApp(self)
        middleware = catalog.get_middleware(
            app.wsgi_app,
            allowed_ext=None,  # All extensions allowed as static files
            autorefresh=True,
        )
        middleware.add_files(root / STATIC_FOLDER, STATIC_URL)
        app.wsgi_app = middleware

        self.catalog = catalog
        self.app = app

    def render(self, name: str, **kw) -> str:
        kw["__file_ext"] = ".md"
        print("📋", f"{name}.md")
        return self.catalog.render(name, **kw)

    def serve(self):
        self.app.run()

    def build(self):
        pass

from distutils import extension
from pathlib import Path

from tcom import Catalog

from .extra import current_path
from .highlight_extension import HighlightExtension
from .md_extension import MarkdownExtension
from .wsgi import WSGIApp

COMPONENTS_FOLDER = "components"
CONTENT_FOLDER = "content"
PATTERN = r"(\..*\.jinja|\.jinja|$)"


class Docs:
    def __init__(self, root: str) -> None:
        root = Path(root).parent
        components_folder = root / COMPONENTS_FOLDER
        content_folder = root / CONTENT_FOLDER
        catalog = Catalog(
            globals={"current_path": current_path},
            filters={"current_path": current_path},
            extension=[HighlightExtension, MarkdownExtension],
            pattern=PATTERN,
        )
        catalog.add_folder(components_folder)
        catalog.add_folder(content_folder)

        app = WSGIApp(self)
        app.wsgi_app = catalog.get_middleware(
            app.wsgi_app,
            autorefresh=app.debug,
        )

        self.catalog = catalog
        self.app = app

    def render(self, name: str, **kw) -> str:
        return self.catalog.render(name **kw)

    def serve(self):
        pass

    def build(self):
        pass

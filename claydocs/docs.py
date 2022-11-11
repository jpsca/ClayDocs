import json
import sys
import shutil
import tempfile
import typing as t
from pathlib import Path
from signal import SIGTERM, signal

from .docs_builder import DocsBuilder
from .docs_render import DocsRender
from .docs_server import DocsServer
from .indexer import Indexer
from .nav import Nav

if t.TYPE_CHECKING:
    from .nav import TPages


VALID_COMMANDS = ("serve", "build", "index")


class Docs(DocsBuilder, DocsRender, DocsServer):
    THEME_FOLDER = "theme"
    COMPONENTS_FOLDER = "components"
    CONTENT_FOLDER = "content"
    STATIC_FOLDER = "static"
    BUILD_FOLDER = "build"
    STATIC_URL = "static"
    THUMBNAILS_URL = "thumbnails"
    DEFAULT_COMPONENT = "Page"

    def __init__(
        self,
        pages: "TPages",
        languages: "t.Optional[dict[str,str]]" = None,
        *,
        root: "t.Union[str,Path]" = ".",
        site_url: str = "/",
        default: str = "",
        globals: "t.Optional[dict[str,t.Any]]" = None,
        filters: "t.Optional[dict[str,t.Any]]" = None,
        tests: "t.Optional[dict[str,t.Any]]" = None,
        extensions: "t.Optional[list]" = None,
        md_extensions: "t.Optional[list[str]]" = None,
        md_ext_config: "t.Optional[dict[str,t.Any]]" = None,
    ) -> None:
        root = Path(root)
        if root.is_file():
            root = root.parent
        self.root = root
        self.theme_folder = root / self.THEME_FOLDER
        self.components_folder = root / self.COMPONENTS_FOLDER
        self.content_folder = root / self.CONTENT_FOLDER
        self.static_folder = root / self.STATIC_FOLDER
        self.build_folder = root / self.BUILD_FOLDER
        self.temp_folder = Path(tempfile.mkdtemp())

        self.nav = Nav(
            self.content_folder,
            pages,
            site_url=site_url,
            languages=languages or {},
            default=default,
        )

        self.indexer = Indexer(self.render)

        super().__init__(
            globals=globals,
            filters=filters,
            tests=tests,
            extensions=extensions,
            md_extensions=md_extensions,
            md_ext_config=md_ext_config,
        )

    def run(self) -> None:
        def sigterm_handler(_, __):
            raise SystemExit(1)

        signal(SIGTERM, sigterm_handler)

        try:
            py, *sysargs = sys.argv
            cmd = sysargs[0] if sysargs else "serve"
            if cmd not in VALID_COMMANDS:
                return self.cmd_help(py)
            if cmd == "serve":
                self.cmd_index()
                self.cmd_serve()
            elif cmd == "build":
                self.cmd_build()
            elif cmd == "index":
                self.cmd_index()
        except Exception:
            raise
        finally:
            shutil.rmtree(self.temp_folder, ignore_errors=True)
            sys.stderr.write("\n")
            exit(1)

    def cmd_serve(self):
        self.serve()

    def cmd_build(self):
        self.build()

    def cmd_index(self):
        pages = list(self.nav.pages.values())
        documents, indexes = self.indexer.index(pages)

        filepath = self.static_folder / "documents.json"
        filepath.write_text(json.dumps(documents))

        for lang, index in indexes.items():
            filepath = self.static_folder / f"search-{lang}.json"
            filepath.write_text(json.dumps(index))

    def cmd_help(self, py: str):
        print("\nValid commands:")
        for cmd in VALID_COMMANDS:
            print(f"  python {py} {cmd}")

import json
import sys
import shutil
import tempfile
import typing as t
from pathlib import Path
from signal import SIGTERM, signal

from .indexer import Indexer
from .docs_builder import DocsBuilder
from .docs_render import DocsRender
from .docs_server import DocsServer
from .nav import DEFAULT_LANG, Nav, TPages
from .utils import logger


VALID_COMMANDS = ("serve", "build", "index")
INDEX_JSON = "search-{lang}.json"


class Docs(DocsBuilder, DocsRender, DocsServer):
    def __init__(
        self,
        pages: TPages,
        *,
        root: str | Path = "./",
        content_folder: str | Path = "",
        languages: dict[str, str] | None = None,
        default: str = DEFAULT_LANG,
        site_url: str = "/",
        search: bool = True,
        cache: bool = True,
        add_ons: list[t.Any] | None = None,
        globals: dict[str, t.Any] | None = None,
        filters: dict[str, t.Any] | None = None,
        tests: dict[str, t.Any] | None = None,
        extensions: list | None = None,
        md_extensions: list[str] | None = None,
        md_ext_config: dict[str, t.Any] | None = None,
        STATIC_FOLDER: str = "static",
        BUILD_FOLDER: str = "build",
        CACHE_FOLDER: str = ".cache",
        STATIC_URL: str = "static",
        THUMBNAILS_URL: str = "thumbnails",
        DEFAULT_COMPONENT: str = "Page",
    ) -> None:
        """
        """
        self.CACHE_FOLDER = CACHE_FOLDER
        self.STATIC_URL = STATIC_URL
        self.THUMBNAILS_URL = THUMBNAILS_URL
        self.DEFAULT_COMPONENT = DEFAULT_COMPONENT

        root = Path(root).resolve()
        if root.is_file():
            root = root.parent
        self.root = root
        logger.debug(f"Root path is {self.root}")

        if content_folder:
            self.content_folder = Path(content_folder).resolve()
        else:
            self.content_folder = self.root / "content"
        logger.debug(f"content_folder is {self.content_folder}")

        self.static_folder = (root / STATIC_FOLDER).resolve()
        logger.debug(f"static_folder is {self.static_folder}")

        self.cache = cache
        if cache:
            self.cache_folder = (root / CACHE_FOLDER).resolve()
            logger.debug(f"cache_folder is {self.cache_folder}")

        self.build_folder = (root / BUILD_FOLDER).resolve()
        self.build_folder_static = self.build_folder / STATIC_FOLDER
        logger.debug(f"build_folder is {self.build_folder}")

        self.content_folder.mkdir(exist_ok=True)
        self.static_folder.mkdir(exist_ok=True)

        self.static_url = f"/{STATIC_URL.lstrip('/')}"
        self.temp_folder = Path(tempfile.mkdtemp())

        self.add_ons = add_ons or []

        self.nav = Nav(
            self.content_folder,
            pages,
            site_url=site_url,
            languages=languages or {},
            default=default,
        )

        self.search = search
        self.indexer = Indexer(self.root, self.render) if search else None

        self.__init_renderer__(
            globals=globals,
            filters=filters,
            tests=tests,
            extensions=extensions,
            md_extensions=md_extensions,
            md_ext_config=md_ext_config,
        )
        print(self.nav.pages)

    def add_folder(self, folder: str | Path, *, prefix: str = "") -> None:
        self.catalog.add_folder(folder, prefix=prefix)

    def add_module(self, module: t.Any, *, prefix: str = "") -> None:
        self.catalog.add_module(module, prefix=prefix)

    def run(self) -> None:
        def sigterm_handler(_, __):
            raise SystemExit(1)

        signal(SIGTERM, sigterm_handler)

        self.__init_server__()

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
        finally:
            shutil.rmtree(self.temp_folder, ignore_errors=True)
            sys.stderr.write("\n")

    def cmd_index(self):
        if not self.search or not self.indexer:
            return
        pages = list(self.nav.pages.values())
        data = self.indexer.index(pages)
        indent = None

        for lang, langdata in data.items():
            filepath = self.static_folder / INDEX_JSON.format(lang=lang)
            filepath.write_text(json.dumps(langdata, indent=indent))

    def cmd_serve(self):
        self.cache_pages()
        self.serve()

    def cmd_build(self):
        self.build()

    def cmd_help(self, py: str):
        print("\nValid commands:")
        for cmd in VALID_COMMANDS:
            print(f"  python {py} {cmd}")

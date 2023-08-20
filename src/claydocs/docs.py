import sys
import shutil
import tempfile
import typing as t
from pathlib import Path
from signal import SIGTERM, signal

from .docs_builder import DocsBuilder
from .docs_render import DocsRender
from .docs_server import DocsServer
from .nav import DEFAULT_LANG, Nav
from .utils import logger

if t.TYPE_CHECKING:
    from .nav import TPages


VALID_COMMANDS = ("serve", "build", "index")


class Docs(DocsBuilder, DocsRender, DocsServer):
    def __init__(
        self,
        pages: "TPages",
        languages: "dict[str, str] | None" = None,
        *,
        root: "str | Path" = "./",
        site_url: str = "/",
        default: str = DEFAULT_LANG,
        add_ons: "list[t.Any] | None" = None,
        globals: "dict[str,t.Any] | None" = None,
        filters: "dict[str,t.Any] | None" = None,
        tests: "dict[str,t.Any] | None" = None,
        extensions: "list | None" = None,
        md_extensions: "list[str] | None" = None,
        md_ext_config: "dict[str, t.Any] | None" = None,

        COMPONENTS_FOLDER: str = "components",
        CONTENT_FOLDER: str = "content",
        STATIC_FOLDER: str = "static",
        THEME_FOLDER: str = "theme",
        BUILD_FOLDER: str = "build",
        CACHE_FOLDER: str = ".cache",
        STATIC_URL: str = "static",
        THUMBNAILS_URL: str = "thumbnails",
        DEFAULT_COMPONENT: str = "T.Page",
    ) -> None:
        self.CACHE_FOLDER = CACHE_FOLDER
        self.STATIC_URL = STATIC_URL
        self.THUMBNAILS_URL = THUMBNAILS_URL
        self.DEFAULT_COMPONENT = DEFAULT_COMPONENT

        root = Path(root).resolve()
        if root.is_file():
            root = root.parent
        self.root = root
        logger.debug(f"Root path is {self.root}")

        self.content_folder = (root / CONTENT_FOLDER).resolve()
        logger.debug(f"content_folder is {self.content_folder}")
        self.content_folder.mkdir(exist_ok=True)

        self.static_folder = (root / STATIC_FOLDER).resolve()
        logger.debug(f"static_folder is {self.static_folder}")
        self.static_folder.mkdir(exist_ok=True)

        self.components_folder = (root / COMPONENTS_FOLDER).resolve()
        logger.debug(f"components_folder is {self.components_folder}")
        if not self.components_folder.is_dir():
            logger.warning(f"{self.components_folder} is not a folder")
            self.components_folder = None

        theme_folder = (root / THEME_FOLDER).resolve()
        if theme_folder.exists():
            self.theme_folder = theme_folder
            logger.debug(f"theme_folder is {theme_folder}")

        self.cache_folder = (root / CACHE_FOLDER).resolve()
        logger.debug(f"cache_folder is {self.cache_folder}")

        self.build_folder = (root / BUILD_FOLDER).resolve()
        self.build_folder_static = self.build_folder / STATIC_FOLDER
        logger.debug(f"build_folder is {self.build_folder}")

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

        self.__init_renderer__(
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

        self.__init_server__()

        try:
            py, *sysargs = sys.argv
            cmd = sysargs[0] if sysargs else "serve"
            if cmd not in VALID_COMMANDS:
                return self.cmd_help(py)
            if cmd == "serve":
                self.cmd_serve()
            elif cmd == "build":
                self.cmd_build()
        finally:
            shutil.rmtree(self.temp_folder, ignore_errors=True)
            sys.stderr.write("\n")

    def cmd_serve(self):
        self.cache_pages()
        self.serve()

    def cmd_build(self):
        self.build()

    def cmd_help(self, py: str):
        print("\nValid commands:")
        for cmd in VALID_COMMANDS:
            print(f"  python {py} {cmd}")

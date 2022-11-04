import shutil
import sys
import tempfile
import typing as t
from pathlib import Path
from signal import SIGTERM, signal

from .docs_builder import DocsBuilder
from .docs_render import DocsRender
from .docs_server import DocsServer
from .nav import Nav

if t.TYPE_CHECKING:
    from .nav import TNavConfig, TLanguages


DEFAULT_LANGUAGE = "en"


class Docs(DocsRender, DocsServer, DocsBuilder):
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
        nav_config: "t.Union[TNavConfig, dict[str,TNavConfig]]",
        languages: "t.Optional[TLanguages]" = None,
        *,
        root: "t.Union[str,Path]" = ".",
        site_url: str = "/",
        default: str = DEFAULT_LANGUAGE,
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

        if not isinstance(nav_config, dict):
            nav_config = {default: nav_config}

        self.nav = Nav(
            self.content_folder,
            nav_config,
            site_url=site_url,
            languages=languages or {},
            default=default,
        )
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
            shutil.rmtree(self.temp_folder, ignore_errors=True)
            sys.stderr.write("\n")
            exit(1)

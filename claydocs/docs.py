import sys
import textwrap
from pathlib import Path
from signal import SIGTERM, signal
from typing import TYPE_CHECKING
from typing import Any
from typing import Optional
from xmlrpc.server import resolve_dotted_attribute

import jinja2
import markdown
from markdown.extensions.toc import slugify_unicode
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
BUILD_FOLDER = "build"

STATIC_URL = "static"
DEFAULT_COMPONENT = "Page"

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
BUILD_MESSAGE = """
─────────────────────────────────────────────────
 Building documentation...
─────────────────────────────────────────────────
"""


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
        self.build_folder = root / BUILD_FOLDER

        self.nav = NavTree(self.content_folder, nav_config)
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
        globals["nav"] = self.nav

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
        filepath = self.content_folder / f"{name}.md"
        if not filepath.exists():
            return ""

        md_source, meta = load_markdown_metadata(filepath)
        meta.update(kw)
        url, nav_page = self.nav.get_page(filepath)
        meta.setdefault("component", DEFAULT_COMPONENT)
        meta.setdefault("title", nav_page["title"])
        meta.setdefault("section", nav_page["section"])
        meta["current_page"] = url

        component = meta["component"]
        content = self.render_markdown(md_source)
        source = "<%(component)s __attrs={attrs}>%(content)s</%(component)s>" % {
            "component": component,
            "content": content,
        }
        return self.catalog.render(component, source=source, **meta)

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
            server = self.get_server()
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

    def get_server(self) -> LiveReloadServer:
        server = LiveReloadServer(render=self.render)

        middleware = self.catalog.get_middleware(
            server.application,
            allowed_ext=None,  # All file extensions allowed as static files
            autorefresh=True,
        )
        middleware.add_files(self.static_folder, STATIC_URL)
        server.application = middleware
        return server

    def build(self) -> None:
        print(BUILD_MESSAGE)

        for url in self.nav.titles:
            name = url.strip("/")
            if name.endswith("/index") or name == "index":
                filename = f"{name}.html"
            else:
                filename = f"{name}/index.html"
            filepath = self.build_folder / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            print(f" - {BUILD_FOLDER}/{filename}")
            html = self.render(name)
            filepath.write_text(html)

        print("\n ✨ Done! ✨  \n")

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
                print(f"""
Valid commands:
  python {py} serve
  python {py} build
""")
        finally:
            sys.stderr.write("\n")
            exit(1)

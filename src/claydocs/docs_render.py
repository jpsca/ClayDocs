import re
import shutil
import textwrap
import typing as t

import inflection
import markdown
from image_processing import ImageProcessing
from pymdownx import emoji
from jinjax.catalog import Catalog
from slugify import slugify

from . import outliner
from .jinja_code import CodeExtension
from .utils import load_markdown_metadata, logger, timestamp, widont

from pathlib import Path
from .utils import Page, THasPaths


DEFAULT_MD_EXTENSIONS = [
    "attr_list",
    "def_list",
    "md_in_html",
    "meta",
    "sane_lists",
    "tables",
    "pymdownx.betterem",
    "pymdownx.caret",
    "pymdownx.emoji",
    "pymdownx.highlight",
    "pymdownx.inlinehilite",
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
    "pymdownx.highlight": {
        "linenums_style": "pymdownx-inline",
        "anchor_linenums": False,
        "css_class": "highlight",
        "linenums": True,
    },
    "pymdownx.emoji": {
        "emoji_generator": emoji.to_alt,
    },
}

UTILS = {
    "camelize": inflection.camelize,
    "humanize": inflection.humanize,
    "ordinal": inflection.ordinal,
    "ordinalize": inflection.ordinalize,
    "parameterize": inflection.parameterize,
    "pluralize": inflection.pluralize,
    "slugify": slugify,
    "singularize": inflection.singularize,
    "titleize": inflection.titleize,
    "underscore": inflection.underscore,
    "widont": widont,
}
DEFAULT_EXTENSIONS = [
    "jinja2.ext.loopcontrols",
    CodeExtension,
]

RX_CODE = re.compile("<code[^>]*>.*?</code>", re.DOTALL)
SOCIAL_SUFFIX = "/og-card.png"


class DocsRender(THasPaths if t.TYPE_CHECKING else object):
    def __init_renderer__(
        self,
        *,
        globals: dict[str, t.Any] | None = None,
        filters: dict[str, t.Any] | None = None,
        tests: dict[str, t.Any] | None = None,
        extensions: list | None = None,
        md_extensions: list[str] | None = None,
        md_ext_config: dict[str, t.Any] | None = None,
    ) -> None:
        self.__init_markdowner__(
            extensions=md_extensions or DEFAULT_MD_EXTENSIONS,
            ext_config=md_ext_config or DEFAULT_MD_EXT_CONFIG,
        )
        self.__init_thumbnailer__()
        self.__init_catalog__(globals, filters, tests, extensions)

    def __init_markdowner__(
        self,
        extensions: list,
        ext_config: dict[str, t.Any],
    ) -> None:
        self.markdowner = markdown.Markdown(
            extensions=extensions,
            extension_configs=ext_config,
            output_format="html",
            tab_length=2,
        )

    def __init_thumbnailer__(self) -> None:
        this = self

        class Thumbnailer(ImageProcessing):
            def __init__(self, source: str) -> None:
                source = source.strip(" /").removeprefix(this.STATIC_URL).strip("/")
                super().__init__(this.static_folder / source)

            def __str__(self) -> str:
                filename = self.get_temp_filename()
                dest = this.temp_folder / filename
                if not dest.is_file():
                    self.save(dest)
                return f"/{this.THUMBNAILS_URL}/{filename}"

            repr = __str__

        self.Thumbnailer = Thumbnailer

    def __init_catalog__(
        self,
        globals: dict[str, t.Any] | None = None,
        filters: dict[str, t.Any] | None = None,
        tests: dict[str, t.Any] | None = None,
        extensions: list | None = None,
    ) -> None:
        _globals = globals or {}
        _globals["utils"] = UTILS.copy()
        _globals["utils"]["thumb"] = self.Thumbnailer

        _filters = filters or {}
        for name, func in UTILS.items():
            _filters[f"utils.{name}"] = func
        _filters["markdown"] = self.markdown_filter

        _tests = tests or {}

        _extensions = extensions or []
        _extensions += DEFAULT_EXTENSIONS[:]

        catalog = Catalog(
            globals=_globals,
            filters=_filters,
            tests=_tests,
            extensions=_extensions,
        )
        catalog.jinja_env.extend(markdowner=self.markdowner)
        logger.debug("Adding folders to catalog...")
        logger.debug(f"Adding content folder: {self.content_folder}")
        catalog.add_folder(self.content_folder)

        for module in self.add_ons:
            logger.debug(f"Adding add-on {module}")
            catalog.add_module(module)

        catalog.jinja_env.autoescape = False
        self.catalog = catalog

    def render(self, url: str) -> str:
        page = self.nav.get_page(url)
        if not page:
            return ""
        return self.render_page(page)

    def render_page(self, page: Page) -> str:
        filepath = self.content_folder / page.filename.strip("/")
        logger.debug(f"Rendering `{filepath}`")

        nav = self.nav.get_page_nav(page)
        md_source, meta = load_markdown_metadata(filepath)
        source = self.render_markdown(md_source)
        source = source.removeprefix("<p>").removesuffix("</p>")

        meta.setdefault("title", nav.page.title)
        self.catalog.jinja_env.globals["nav"] = nav
        self.catalog.jinja_env.globals["meta"] = meta
        self.catalog.jinja_env.globals["utils"]["timestamp"] = timestamp()

        html = self.catalog.render("", __source=source)
        html, page_toc = outliner.outline(html)
        nav.page_toc = page_toc
        component = meta.get("component", self.default_component)
        # I use `catalog.irender` to not reset the assets collected in rendering
        # the content
        return self.catalog.irender(component, __content=html)

    def render_social_card(self, page: Page) -> str:
        component = page.meta.get("social_card", self.default_social)
        return self.catalog.render(component, page=page)

    def render_markdown(self, md_source: str) -> str:
        md_source = self.anti_escape(md_source)
        md_source = textwrap.dedent(md_source.strip("\n")).strip()
        html = self.markdowner.convert(md_source)
        html = html.replace("<pre><span></span>", "<pre>")
        html = self.escape_jinja_in_code(html)
        return html

    def markdown_filter(self, source: str) -> str:
        html = self.render_markdown(source)
        return html

    def anti_escape(self, s: str, /) -> str:
        return (
            s
            .replace("&amp;", "&")
            .replace("&gt;", ">")
            .replace("&lt;", "<")
            .replace("&#39;", "'")
            .replace("&#34;", '"')
        )

    def escape_jinja_in_code(self, html: str) -> str:
        def escape_block(match: re.Match[str]) -> str:
            return (
                match.group(0)
                .replace("{", "&#123;")
                .replace("}", "&#125;")
            )

        return RX_CODE.sub(escape_block, html)

    def cache_pages(self) -> None:
        if self.cache:
            shutil.rmtree(self.cache_folder, ignore_errors=True)
            self.cache_folder.mkdir()

        for url in self.nav.pages:
            page = self.nav.get_page(url)
            if not page:
                logger.error(f"Page not found: {url}")
                continue
            self.cache_page(page)

    def cache_page(self, page: Page) -> str:
        html = self.render_page(page)
        if self.cache:
            filepath = self.get_cache_path(page)
            filepath.write_text(html)
            page.cache_path = filepath
        return html

    def get_cache_path(self, page: Page) -> "Path":
        filename = page.url.strip("/")
        filename = f"{filename}/index.html".lstrip("/")
        filepath = self.cache_folder / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        return filepath

    def get_cached_page(self, url: str) -> str:
        social = url.endswith(SOCIAL_SUFFIX)
        if social:
            url = url.removesuffix(SOCIAL_SUFFIX)

        page = self.nav.get_page(url)
        if not page:
            return ""

        if social:
            return self.render_social_card(page)

        if not page.cache_path or not page.cache_path.exists():
            return self.cache_page(page)
        else:
            assert page.cache_path
            return page.cache_path.read_text()

    def refresh(self, src_path: str) -> None:
        if self.cache and src_path.endswith((".md", ".jinja")):
            self.cache_pages()

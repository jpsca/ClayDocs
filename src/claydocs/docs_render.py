import textwrap
import typing as t

from image_processing import ImageProcessing
import inflection
import markdown
from pymdownx import emoji
from markupsafe import Markup
from markdown.extensions.toc import slugify_unicode  # type: ignore
from jinjax.catalog import Catalog

from .jinja_code import CodeExtension
from .jinja_markdown import MarkdownExtension
from .utils import load_markdown_metadata, logger, timestamp, widont

if t.TYPE_CHECKING:
    from .nav import Page
    from .utils import THasPaths


DEFAULT_MD_EXTENSIONS = [
    "attr_list",
    "def_list",
    "md_in_html",
    "meta",
    "sane_lists",
    "tables",
    "toc",
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
    "toc": {
        "marker": "",
        "anchorlink": False,
        "permalink": True,
        "slugify": slugify_unicode,
    },
    "pymdownx.highlight": {
        "linenums_style": "pymdownx-inline",
        "anchor_linenums": True,
        "css_class": "highlight not-prose",
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
    "singularize": inflection.singularize,
    "titleize": inflection.titleize,
    "underscore": inflection.underscore,
    "widont": widont,
}
DEFAULT_EXTENSIONS = [
    "jinja2.ext.loopcontrols",
    CodeExtension,
    MarkdownExtension,
]


class DocsRender(THasPaths if t.TYPE_CHECKING else object):
    def __init_renderer__(
        self,
        *,
        globals: "t.Optional[dict[str,t.Any]]" = None,
        filters: "t.Optional[dict[str,t.Any]]" = None,
        tests: "t.Optional[dict[str,t.Any]]" = None,
        extensions: "t.Optional[list]" = None,
        md_extensions: "t.Optional[list[str]]" = None,
        md_ext_config: "t.Optional[dict[str,t.Any]]" = None,
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
        globals: "t.Optional[dict[str,t.Any]]" = None,
        filters: "t.Optional[dict[str,t.Any]]" = None,
        tests: "t.Optional[dict[str,t.Any]]" = None,
        extensions: "t.Optional[list]" = None,
    ) -> None:
        _globals = globals or {}
        _globals["utils"] = UTILS.copy()
        _globals["utils"]["thumb"] = self.Thumbnailer

        _filters = filters or {}
        for name, func in UTILS.items():
            _filters[f"utils.{name}"] = func

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

        if self.components_folder:
            logger.debug(f"Adding components folder: {self.components_folder}")
            catalog.add_folder(self.components_folder)
        else:
            logger.debug("Missing components folder")

        if self.theme_folder:
            logger.debug(f"Adding theme folder: {self.theme_folder}")
            catalog.add_folder(self.theme_folder)
        else:
            logger.debug("Missing theme folder")

        for module in self.add_ons:
            logger.debug(f"Adding add-on {module.components_path}")
            catalog.add_module(module)

        self.catalog = catalog

    def render(self, url: str, **kw) -> str:
        page = self.nav.get_page(url)
        if not page:
            return ""
        return self.render_page(page, **kw)

    def render_page(self, page: "Page", **kw) -> str:
        filepath = self.content_folder / page.filename.strip("/")
        logger.debug(f"Rendering `{filepath}`")
        md_source, meta = load_markdown_metadata(filepath)
        nav = self.nav.get_page_nav(page)
        nav.search = self.search
        content = self.render_markdown(md_source)
        nav.page_toc = self.nav._get_page_toc(self.markdowner.toc_tokens)  # type: ignore
        component = meta.get("component", self.DEFAULT_COMPONENT)
        source = (
            '{%% %(component)s title="%(title)s" %%}\n'
            "<!--startpage-->\n"
            "%(content)s"
            "\n<!--endpage-->"
            "\n{%% end%(component)s %%}"
        ) % {
            "title": nav.page.title,
            "component": component,
            "content": content,
        }
        self.catalog.jinja_env.globals["nav"] = nav
        self.catalog.jinja_env.globals["meta"] = meta
        self.catalog.jinja_env.globals["utils"]["timestamp"] = timestamp()
        return self.catalog.render(component, __source=source, **kw)

    def render_markdown(self, source: str) -> Markup:
        source = textwrap.dedent(source.strip("\n"))
        html = (
            self.markdowner.convert(source)
            .replace("<code", "{% raw %}<code")
            .replace("</code>", "</code>{% endraw %}")
        )
        return Markup(html)

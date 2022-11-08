import textwrap
import typing as t

from image_processing import ImageProcessing
import inflection
import markdown
from pymdownx import emoji
from markupsafe import Markup
from markdown.extensions.toc import slugify_unicode  # type: ignore
from tcom.catalog import Catalog

from .utils import load_markdown_metadata, logger, timestamp

if t.TYPE_CHECKING:
    from .utils import THasPaths


DEFAULT_MD_EXTENSIONS = [
    "attr_list",
    "def_list",
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
        "toc_class": "",
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
}
DEFAULT_EXTENSIONS = [
    "jinja2.ext.loopcontrols",
]


class DocsRender(THasPaths if t.TYPE_CHECKING else object):
    def __init__(
        self,
        *,
        globals: "t.Optional[dict[str,t.Any]]" = None,
        filters: "t.Optional[dict[str,t.Any]]" = None,
        tests: "t.Optional[dict[str,t.Any]]" = None,
        extensions: "t.Optional[list]" = None,
        md_extensions: "t.Optional[list[str]]" = None,
        md_ext_config: "t.Optional[dict[str,t.Any]]" = None,
    ) -> None:
        self.markdowner = markdown.Markdown(
            extensions=md_extensions or DEFAULT_MD_EXTENSIONS,
            extension_configs=md_ext_config or DEFAULT_MD_EXT_CONFIG,
            output_format="html",
            tab_length=2,
        )
        self.__init_thumbnailer__()
        self.__init_catalog__(globals, filters, tests, extensions)

    def __init_thumbnailer__(self) -> None:
        this = self

        class Thumbnailer(ImageProcessing):
            def __init__(self, source: str) -> None:
                source = source.strip(" /").removeprefix(this.STATIC_URL).strip("/")
                super().__init__(this.static_folder / source)

            def __str__(self) -> str:
                ops = str(self.options).encode("utf8", errors="ignore")
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
        _filters["utils"] = UTILS.copy()

        _tests = tests or {}

        _extensions = extensions or []
        _extensions += DEFAULT_EXTENSIONS

        catalog = Catalog(
            globals=_globals,
            filters=_filters,
            tests=_tests,
            extensions=_extensions,
        )
        catalog.add_folder(self.content_folder)
        catalog.add_folder(self.components_folder)
        catalog.add_folder(self.theme_folder)
        self.catalog = catalog

    def render(self, url: str, **kw) -> str:
        page = self.nav.get_page(url)
        if not page:
            return ""

        filepath = self.content_folder / page.filename
        logger.debug(f"Rendering `{filepath}`")

        md_source, meta = load_markdown_metadata(filepath)
        nav = self.nav.get_page_nav(page)
        content = self.render_markdown(md_source)
        nav.page_toc = self.nav._get_page_toc(self.markdowner.toc_tokens)  # type: ignore
        component = meta.get("component", self.DEFAULT_COMPONENT)
        source = (
            '<%(component)s title="%(title)s">%(content)s</%(component)s>'
         ) % {
            "title": nav.page.title,
            "component": component,
            "content": content,
        }

        self.catalog.jinja_env.globals["nav"] = nav
        self.catalog.jinja_env.globals["meta"] = nav.page.meta
        self.catalog.jinja_env.globals["utils"]["timestamp"] = timestamp()
        return self.catalog.render(component, source=source, **kw)

    def render_markdown(self, source: str) -> Markup:
        source = textwrap.dedent(source.strip("\n"))
        html = (
            self.markdowner.convert(source)
            .replace("<code", "{% raw %}<code")
            .replace("</code>", "</code>{% endraw %}")
        )
        return Markup(html)

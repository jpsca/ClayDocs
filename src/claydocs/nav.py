import json
import os
import re
import typing as t
from dataclasses import asdict, dataclass
from pathlib import Path

from slugify import slugify

from .exceptions import InvalidNav
from .utils import Page, load_markdown_metadata, logger



TPagesBranch = t.Sequence[str | tuple[str, "TPagesBranch"]]
TPagesMultiLang = dict[str, TPagesBranch]
TPages = TPagesBranch | TPagesMultiLang
TStrOrPath = str | Path

DEFAULT_LANG = "en"
rx_markdwown_h1 = re.compile(r"(^|\n)#\s+(?P<h1>[^\n]+)(\n|$)")
rx_html_h1 = re.compile(r"<h1>(?P<h1>.+)</h1>", re.IGNORECASE)



@dataclass
class Language:
    code: str
    url: str = ""
    name: str = ""


@dataclass
class PageNav:
    page: Page
    prev_page: Page
    next_page: Page
    toc: list
    page_toc: list
    languages: list[Language]
    base_url: str = ""


class Nav:
    def __init__(
        self,
        content_folder: TStrOrPath,
        pages: TPages,
        *,
        site_url: str = "",
        languages: dict[str, str] | None = None,
        default: str = DEFAULT_LANG,
    ) -> None:
        self.pages: dict[str, Page] = {}
        self.languages: dict[str, Language] = {}
        self.toc: dict[str, list] = {}
        self.urls: dict[str, list[str]] = {}
        self._max_index: dict[str, int] = {}

        self._content_folder = Path(content_folder)
        site_url = site_url.strip() or "/"
        if site_url != "/":
            site_url = f"/{site_url.strip('/')}/"
        self.site_url = site_url
        self.default = default

        if isinstance(pages, dict):
            self._init_multi_language(pages, languages or {})
        else:
            self._init_single_language(pages, default)

        self._log_initial_status()

    def _init_multi_language(
        self,
        pages: TPagesMultiLang,
        languages: dict[str, str],
    ) -> None:
        self.languages = self._build_languages(languages)

        for lang in languages:
            self.toc[lang] = []
            self.urls[lang] = []
            if lang == self.default:
                base_url = self.site_url
            else:
                base_url = f"{self.site_url}{lang}/"

            self._index_pages(
                pages[lang],
                lang=lang,
                base_url=base_url,
                root=lang,
                section=self.toc[lang],
            )
            self._max_index[lang] = len(self.urls[lang]) - 1

    def _init_single_language(
        self,
        pages: TPagesBranch,
        default: str,
    ) -> None:
        self.toc[default] = []
        self.urls[default] = []
        self._index_pages(
            pages,
            lang=default,
            base_url=self.site_url,
            root="",
            section=self.toc[default],
        )
        self._max_index[default] = len(self.urls[default]) - 1

    def get_page(self, url: str) -> Page | None:
        return self.pages.get(url) or self.pages.get(f"{url}/") or None

    def get_page_nav(self, page: Page) -> PageNav:
        prev_page = self._get_prev(page.url, lang=page.lang)
        next_page = self._get_next(page.url, lang=page.lang)
        toc = self.toc[page.lang]

        if self.languages:
            base_url = self.languages[page.lang].url
            languages = list(self.languages.values())
        else:
            base_url = "/"
            languages = []

        return PageNav(
            page=page,
            prev_page=prev_page,
            next_page=next_page,
            toc=toc,
            page_toc=[],
            base_url=base_url,
            languages=languages,
        )

    # Private

    def _build_languages(self, languages: dict[str, str]) -> dict[str, Language]:
        """
        Takes a dict of `code: Name` pairs and improves it with the
        root of the language content.

        Example input:

        ```python
        {
            "en": "English",
            "es": "Español",
        }
        ```

        Example output:

        ```python
        {
            "en": Language(code="en", url="/", name="English"),
            "es": Language(code="es", url="/es/", name="Español"),
        }
        ```
        """
        langs = {}
        for code, name in languages.items():
            if code == self.default:
                url = self.site_url
            else:
                url = f"{self.site_url}{code}/"
            langs[code] = Language(code=code, url=url, name=name)

        return langs

    def _index_pages(
        self,
        pages: TPagesBranch,
        *,
        lang: str,
        base_url: str,
        root: str,
        section_title: str = "",
        section: list,
    ) -> None:
        """
        Recursively process the pages list to build the table of contents
        and extract the pages metadata.

        The titles are extracted from the contents of each file.

        Example input:

        ```python
        [
            "index.md",
            [
                "Guide",
                [
                    "guide/index.md",
                    "guide/arguments.md",
                    "guide/extra.md",
                ],
            ],
            "faq.md",
        ]
        ```

        Example output:

        ```python
        # self.toc
        {
            LANG: [
                ["/index", "Home"],
                [null, "Guide", [
                    ["/guide/index", "The Guide"],
                    ["/guide/arguments", "The Arguments"],
                    ["/guide/extra", "Extra arguments"],
                ]],
                ["/faq", "FAQ"],
            ],
            ...
        }

        # self.pages
        {
            "/index":
                <Page
                    lang="en" url="/index", root="en/index.md",
                    title="Home", index=0, section="", meta={...}
                >,
            "/guide/index":
                <Page
                    lang="en" url="/guide/index", root="en/guide/index.md",
                    title="The Guide", index=1, section="Guide", meta={...}
                >,
            "/guide/arguments":
                <Page
                    lang="en" url="/guide/arguments", root="en/guide/arguments.md",
                    title="The Arguments", index=2, section="Guide", meta={...}
                >,
            "/guide/extra":
                <Page
                    lang="en" url="/guide/extra", root="en/guide/extra.md",
                    title="Extra arguments", index=3, section="Guide", meta={...}
                >,
            "/faq":
                <Page
                    lang="en" url="/faq", root="en/faq.md",
                    title="FAQ", index=4, section="", meta={...}
                >,
            },
        }

        # self.urls
        {
            "en": [
                "/index",
                "/guide/index",
                "/guide/arguments",
                "/guide/extra",
                "/faq",
            ]
        }
        ```
        """
        for item in pages:
            if isinstance(item, str):
                self._index_page(
                    item,
                    lang=lang,
                    base_url=base_url,
                    root=root,
                    section_title=section_title,
                    section=section,
                )

            elif isinstance(item, (tuple, list)) and len(item) == 2:
                self._index_section(
                    tuple(item),  # type: ignore
                    lang=lang,
                    base_url=base_url,
                    root=root,
                    section=section,
                )

            else:
                raise InvalidNav(item)

    def _index_page(
        self,
        item: str,
        *,
        lang: str,
        base_url: str,
        root: str,
        section_title: str,
        section: list,
    ) -> None:
        filepath = self._content_folder / root / item
        source, meta = load_markdown_metadata(filepath)
        title = (
            meta.pop("title", None) or self._extract_page_title(source) or filepath.name
        )
        slug = meta.get("slug") or item
        url = f"{base_url}{self._get_url(slug)}"

        index = len(self.urls[lang])
        self.pages[url] = Page(
            lang=lang,
            url=url,
            filename=f"{root}/{item}".strip("/"),
            title=title,
            index=index,
            section=section_title,
            meta=meta,
        )
        self.urls[lang].append(url)
        section.append([url, title, None])

    def _index_section(
        self,
        item: tuple[str, TPagesBranch],
        *,
        lang: str,
        base_url: str,
        root: str,
        section: list,
    ) -> None:
        section_title, subpages = item

        section_title = section_title.strip()
        new_section = [None, section_title, []]
        section.append(new_section)
        self._index_pages(
            pages=subpages,
            lang=lang,
            base_url=base_url,
            root=root,
            section_title=section_title,
            section=new_section[-1],
        )

    def _extract_page_title(self, source: str) -> str:
        match = rx_markdwown_h1.search(source)
        if match:
            return match.group("h1")

        match = rx_html_h1.search(source)
        if match:
            return match.group("h1")

        return ""

    def _get_prev(self, url: str, lang: str = "") -> Page:
        index = self.pages[url].index
        if index <= 0:
            return Page()
        lang = lang or self.default
        prev_url = self.urls[lang][index - 1]
        return self.pages[prev_url]

    def _get_next(self, url: str, lang: str = "") -> Page:
        lang = lang or self.default
        index = self.pages[url].index
        if index >= self._max_index[lang]:
            return Page()

        next_url = self.urls[lang][index + 1]
        return self.pages[next_url]

    def _get_page_toc(self, toc_tokens: dict) -> list:
        """Takes the `toc_tokens` attribute from the "toc" markdown extension,
        and generates an structure, similar to the global toc.

        Example input:
        ```
        [
            {
                "level": 1,
                "id": "t1",
                "name": "T1",
                "children": [
                    {"level": 2, "id": "t2a", "name": "T2A", "children": []},
                    {
                        "level": 2,
                        "id": "t2b",
                        "name": "T2C",
                        "children": [
                            {"level": 3, "id": "t3a", "name": "T3B", "children": []},
                            {"level": 3, "id": "t3b", "name": "T3C", "children": []},
                        ],
                    },
                    {"level": 2, "id": "t2c", "name": "T2C", "children": []},
                ],
            },
        }
        ```

        Example output:
        ```
        [
            ["#t1", "T1", [
                ["#t2a", "T2A", []],
                ["#t2b", "T2B", [
                    ["#t3a", "T3A", []],
                    ["#t3b", "T3B", []],
                ]],
                ["#t2c", "T2C", []],
            ]]
        ]
        ```
        """
        page_toc = []

        def parse_level(tokens, headers):
            for tok in tokens:
                header = [f"#{tok['id']}", tok["name"], []]
                headers.append(header)
                if tok["children"]:
                    parse_level(tok["children"], header[2])

        parse_level(toc_tokens, page_toc)
        return page_toc

    def _get_url(self, filename: str) -> str:
        url = filename.strip(" /").removesuffix(".md").removesuffix("index")
        return "/".join([slugify(part) for part in url.split("/")])

    def _log_initial_status(self) -> None:
        for name in "pages,toc,languages".split(","):
            log_data = json.dumps(
                getattr(self, name),
                default=lambda o: asdict(o),
                ensure_ascii=False,
                indent=2,
            )
            logger.debug(f"self.{name}:\n{log_data}\n")


INDEX = "index.md"


def get_pages_in_folder(path: TStrOrPath) -> TPages:
    def recursive_listdir(path, prefix=""):
        items = []
        for item_name in sorted(os.listdir(path)):
            item_prefixed = os.path.join(prefix, item_name)
            item_path = os.path.join(path, item_name)
            if os.path.isfile(item_path):
                if item_name.endswith(".md"):
                    items.append(item_prefixed)
            else:
                item = recursive_listdir(item_path, prefix=item_prefixed)
                items.append(item)

        if INDEX in items:
            items.remove(INDEX)
            items.insert(0, INDEX)
        return [os.path.basename(path), items]

    return recursive_listdir(str(path))[1]

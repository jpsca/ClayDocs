import json
import re
import typing as t
from dataclasses import asdict, dataclass
from pathlib import Path

from .exceptions import InvalidNav
from .utils import load_markdown_metadata, logger


TPagesBranch = t.Sequence[t.Union[str, t.Sequence]]
TPagesMultiLang = dict[str,TPagesBranch]
TPages = t.Union[TPagesBranch, TPagesMultiLang]
TStrOrPath = t.Union[str, Path]


@dataclass
class Language:
    code: str
    root: str = ""
    name: str = ""


@dataclass
class Page:
    lang: str = ""
    url: str = ""
    filename: str = ""
    title: str = ""
    index: int = 0
    section: str = ""


@dataclass
class PageNav:
    page: Page
    prev_page:  Page
    next_page: Page
    toc: list
    page_toc: list
    languages: list[Language]
    base_url: str = ""


rx_markdwown_h1 = re.compile(r"(^|\n)#\s+(?P<h1>[^\n]+)(\n|$)")
rx_html_h1 = re.compile(r"<h1>(?P<h1>.+)</h1>", re.IGNORECASE)


class Nav:
    def __init__(
        self,
        content_folder: "TStrOrPath",
        pages: "TPages",
        site_url: str,
        languages: "dict[str, str]",
        default: str
    ) -> None:
        self.pages: dict[str, Page] = {}
        self.toc: dict[str, list] = {}
        self.urls: dict[str, list[str]] = {}
        self.languages: dict[str, Language] = {}
        self._max_index: dict[str, int] = {}

        self._content_folder = Path(content_folder)
        site_url = site_url.strip() or "/"
        if site_url != "/":
            site_url = f"/{site_url.strip('/')}/"
        self.site_url = site_url

        default = default.strip('/')
        self.default = default

        if languages:
            assert isinstance(pages, dict)
            self._init_multi_language(pages, languages)
        else:
            assert not isinstance(pages, dict)
            self._init_single_language(pages, default)

        self._log_initial_status()

    def _init_multi_language(
        self,
        pages: "TPagesMultiLang",
        languages: "dict[str, str]",
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
        pages: "TPagesBranch",
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

    def get_page(self, url: str) -> "t.Optional[Page]":
        return self.pages.get(url) \
            or self.pages.get(f"{url}/index") \
                or None

    def get_page_nav(self, page: "Page") -> "PageNav":
        prev_page = self._get_prev(page.url, lang=page.lang)
        next_page = self._get_next(page.url, lang=page.lang)
        toc = self.toc[page.lang]
        base_url = self.languages[page.lang].root
        languages = list(self.languages.values())

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

    def _build_languages(self, languages: "dict[str, str]") -> "dict[str, Language]":
        langs = {}
        for code, name in languages.items():
            if code == self.default:
                root = self.site_url
            else:
                root = f"{self.site_url}{code}/"
            langs[code] = Language(code=code, root=root, name=name)

        return langs

    def _index_pages(
        self,
        pages: "TPages",
        *,
        lang: str,
        base_url: str,
        root: str,
        section_title: str = "",
        section: "list",
    ) -> None:
        """Takes a pages and recursively builds the table of contents.
        The titles not specified are extracted from the contents of each file.

        Example input:

        ```
        [
            "index.md",
            [
                "Guide",
                [
                    "guide/index.md",
                    ["guide/arguments.md", "The Arguments"],
                    "guide/extra.md",
                ],
            ],
            ["faq.md", "FAQ"],
        ]
        ```

        Example output:
        ```
        # self.toc
        {
            LANG: [
                ["/index", "Home", []],
                ["", "Guide", [
                    ["/guide/index", "The Guide"],
                    ["/guide/arguments", "The Arguments"],
                    ["/guide/extra", "Extra arguments"],
                ]],
                ["/faq", "FAQ", []],
            ],
            ...
        }

        # self.pages
        {
            en: {
                "/index":
                    <Page
                        url="/index",
                        root="en/index.md",
                        title="Home",
                        index=0,
                        section="">,
                "/guide/index":
                    <Page
                        url="/guide/index",
                        root="en/guide/index.md",
                        title="The Guide",
                        index=1,
                        section="Guide">,
                "/guide/arguments":
                    <Page
                        url="/guide/arguments",
                        root="en/guide/arguments.md",
                        title="The Arguments",
                        index=2,
                        section="Guide">,
                "/guide/extra":
                    <Page
                        url="/guide/extra",
                        root="en/guide/extra.md",
                        title="Extra arguments",
                        index=3,
                        section="Guide">,
                "/faq":
                    <Page
                        url="/faq",
                        root="en/faq.md",
                        title="FAQ",
                        index=4,
                        section="">,
            },
            ...
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
        tuple_or_list = (tuple, list)

        for item in pages:
            if isinstance(item, str):
                title = self._extract_page_title(root, item)
                url = f"{base_url}{self._get_url(item)}"

                index = len(self.urls[lang])
                self.pages[url] = Page(
                    lang=lang,
                    url=url,
                    filename=f"{root}/{item}",
                    title=title,
                    index=index,
                    section=section_title,
                )
                self.urls[lang].append(url)
                section.append([url, title, None])

            elif isinstance(item, tuple_or_list) and len(item) == 2:
                key, value = item
                if isinstance(value, str):
                    value = value.strip()
                    url = f"{base_url}/{self._get_url(key)}"

                    index = len(self.urls[lang])
                    self.pages[url] = Page(
                        lang=lang,
                        url=url,
                        filename=f"{root}/{key}",
                        title=value,
                        index=index,
                        section=section_title,
                    )
                    self.urls[lang].append(url)
                    section.append([url, value, None])

                elif isinstance(item, tuple_or_list):
                    new_section_title = key.strip()
                    new_section = [None, new_section_title, []]
                    section.append(new_section)
                    self._index_pages(
                        pages=value,
                        lang=lang,
                        base_url=base_url,
                        root=root,
                        section_title=new_section_title,
                        section=new_section[-1],
                    )

                else:
                    raise InvalidNav(item)
            else:
                raise InvalidNav(item)

    def _get_prev(self, url: str, lang: str = "") -> "Page":
        index = self.pages[url].index
        if index <= 0:
            return Page()
        lang = lang or self.default
        prev_url = self.urls[lang][index - 1]
        return self.pages[prev_url]

    def _get_next(self, url: str, lang: str = "") -> "Page":
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
        return filename.strip(" /").removesuffix(".md")
        return f"/{filename}"

    def _extract_page_title(self, root, path: str) -> str:
        filename = self._content_folder / root / path
        source, meta = load_markdown_metadata(filename)
        title = meta.get("title")
        if title:
            return title

        match = rx_markdwown_h1.search(source)
        if match:
            return match.group("h1")

        match = rx_html_h1.search(source)
        if match:
            return match.group("h1")

        return filename.name

    def _log_initial_status(self) -> None:
        for name in "pages,toc,languages".split(","):
            log_data = json.dumps(
                getattr(self, name),
                default=lambda o: asdict(o),
                ensure_ascii=False,
                indent=2,
            )
            logger.debug(f"self.{name}:\n{log_data}\n")

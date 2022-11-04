import json
import re
import typing as t
from dataclasses import dataclass
from pathlib import Path

from .exceptions import InvalidNav
from .utils import load_markdown_metadata, logger


TNavConfig = t.Sequence[t.Union[str, t.Sequence]]
TLanguages = dict[str, str]
TStrOrPath = t.Union[str, Path]


@dataclass
class Page:
    lang: str = ""
    url: str = ""
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
    languages: TLanguages
    lang: str
    base_url: str = ""


rx_markdwown_h1 = re.compile(r"(^|\n)#\s+(?P<h1>[^\n]+)(\n|$)")
rx_html_h1 = re.compile(r"<h1>(?P<h1>.+)</h1>", re.IGNORECASE)


class Nav:
    def __init__(
        self,
        content_folder: "TStrOrPath",
        nav_config: "dict[str,TNavConfig]",
        site_url: str,
        languages: "TLanguages",
        default: str
    ) -> None:
        self._content_folder = Path(content_folder)
        self.titles: dict[str, dict[str, Page]] = {}
        self.toc: dict[str, list] = {}
        self.languages = languages
        self.default = default.strip('/')

        site_url = site_url.strip() or "/"
        if site_url != "/":
            site_url = f"/{site_url.strip('/')}/"
        self.site_url = site_url

        self._urls: dict[str, tuple[str, ...]] = {}
        self._max_index: dict[str, int] = {}

        if languages:
            for lang in languages:
                self.titles[lang] = {}
                self.toc[lang] = []
                self.build_toc(
                    nav_config[lang],
                    lang=lang,
                    root=lang,
                    section=self.toc[lang],
                )
        else:
            self.titles[default] = {}
            self.toc[default] = []
            self.build_toc(
                nav_config[default],
                lang=default,
                root="",
                section=self.toc[default],
            )

        self._urls = {
            lang: tuple(self.titles[lang].keys())
            for lang in languages
        }
        self._max_index = {
            lang: len(self._urls[lang]) - 1
            for lang in languages
        }

        log_titles = json.dumps(
            {
                key: {url: str(page) for url, page in titles.items()}
                for key, titles in self.titles.items()
            },
            indent=2,
        )
        logger.debug(f"Titles\n{log_titles}")

        log_toc = json.dumps(self.toc, indent=2)
        logger.debug(f"TOC\n{log_toc}")

    def build_toc(
        self,
        nav_config: "TNavConfig",
        *,
        lang: str,
        root: str,
        section_title: str = "",
        section: "list",
    ) -> None:
        """Takes a nav_config and recursively builds the table of contents.
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

        # self.titles
        {
            LANG: {
                "/index":
                    <Page url="/index", title="Home", index=0, section="">,
                "/guide/index":
                    <Page url="/guide/index", title="The Guide", index=1, section="Guide">,
                "/guide/arguments":
                    <Page url="/guide/arguments", title="The Arguments", index=2, section="Guide">,
                "/guide/extra":
                    <Page url="/guide/extra", title="Extra arguments", index=3, section="Guide">,
                "/faq":
                    <Page url="/faq", title="FAQ", index=4, section="">,
            },
            ...
        }
        ```
        """
        tuple_or_list = (tuple, list)
        base_url = f"/{root}" if root else root

        for item in nav_config:
            if isinstance(item, str):
                title = self._extract_page_title(root, item)
                url = f"{base_url}{self._get_url(item)}"
                index = len(self.titles[lang].keys())
                self.titles[lang][url] = Page(
                    url=url, title=title, index=index, section=section_title
                )
                section.append([url, title, None])

            elif isinstance(item, tuple_or_list) and len(item) == 2:
                key, value = item
                if isinstance(value, str):
                    value = value.strip()
                    url = f"{base_url}/{self._get_url(key)}"
                    index = len(self.titles[lang].keys())
                    self.titles[lang][url] = Page(
                        url=url, title=value, index=index, section=section_title
                    )
                    section.append([url, value, None])

                elif isinstance(item, tuple_or_list):
                    new_section_title = key.strip()
                    new_section = [None, new_section_title, []]
                    section.append(new_section)
                    self.build_toc(
                        nav_config=value,
                        lang=lang,
                        root=root,
                        section_title=new_section_title,
                        section=new_section[-1],
                    )

                else:
                    raise InvalidNav(item)
            else:
                raise InvalidNav(item)

    def get_lang(self, url: str) -> "tuple[str,str,str]":
        url = self._get_url(url)
        if not self.languages:
            return self.default, self.site_url, ""

        for code in self.languages:
            if code == self.default:
                continue
            prefix = f"{code.strip('/')}/"
            if url.startswith(prefix):
                return code, f"{self.site_url}{prefix}", code

        return self.default, self.site_url, self.default

    def get_prev(
        self,
        lang: str,
        *,
        filename: "TStrOrPath" = "",
        url: str = "",
    ) -> "Page":
        url = url or self._get_url(filename)
        index = self.titles[lang][url].index
        if index <= 0:
            return Page()

        prev_url = self._urls[lang][index - 1]
        return self.titles[lang][prev_url]

    def get_next(
        self,
        lang: str,
        *,
        filename: "TStrOrPath" = "",
        url: str = "",
    ) -> "Page":
        url = url or self._get_url(filename)
        index = self.titles[lang][url].index
        if index >= self._max_index[lang]:
            return Page()

        next_url = self._urls[lang][index + 1]
        return self.titles[lang][next_url]

    def get_page_toc(self, toc_tokens: dict) -> list:
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

    def get_page_nav(self, lang: str, filename: str) -> "PageNav":
        url = self._get_url(filename)
        page = self.titles[lang].get(url) or Page()

        prev_page = self.get_prev(lang, url=url)
        next_page = self.get_next(lang, url=url)
        toc = self.toc[lang]
        page_toc = self.get_page_toc(self.markdowner.toc_tokens)  # type: ignore

        return PageNav(
            page=page,
            page_toc=page_toc,
            prev_page=prev_page,
            next_page=next_page,
            toc=toc,
            languages=self.languages,
            lang=lang,
        )

    # Private

    def _get_url(self, filename: "TStrOrPath") -> str:
        filename = str(filename).strip(" /").removesuffix(".md")
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

import json
import re
import typing as t
from pathlib import Path

from .exceptions import InvalidNav
from .utils import load_markdown_metadata, logger

if t.TYPE_CHECKING:
    TNavConfig = t.Sequence[t.Union[str, t.Sequence]]
    TStrOrPath = t.Union[str, Path]

rx_markdwown_h1 = re.compile(r"(^|\n)#\s+(?P<h1>[^\n]+)(\n|$)")
rx_html_h1 = re.compile(r"<h1>(?P<h1>.+)</h1>", re.IGNORECASE)


class Nav:
    __slots__ = (
        "titles",
        "sections",
        "toc",
        "page_toc",
        "_content_folder",
        "_urls",
        "_max_index",
    )

    def __init__(
        self,
        content_folder: "TStrOrPath",
        nav_config: "TNavConfig",
    ) -> None:
        self._content_folder = Path(content_folder)
        self.titles: dict[str, dict] = {}
        self.sections: list[str] = []
        self.toc = []
        self.build_toc(nav_config, section=self.toc)
        self._urls = tuple(self.titles.keys())
        self._max_index = len(self._urls) - 1

        logger.debug(f"Sections\n{self.sections}")
        log_titles = json.dumps(self.titles, indent=2)
        logger.debug(f"Titles\n{log_titles}")
        logger.debug(f"TOC\n{self.toc}")

    def get_page(self, filepath: "TStrOrPath") -> dict:
        url = self._get_url(filepath)
        return self.titles.get(url) or {
            "url": url,
            "title": "",
            "section": "",
            "index": None,
        }

    def get_prev(
        self,
        filepath: "TStrOrPath" = "",
        url: str = "",
    ) -> dict:
        url = url or self._get_url(filepath)
        index = self.titles[url]["index"]
        if index <= 0:
            return {
                "url": "",
                "title": "",
                "section": "",
                "index": None,
            }

        prev_url = self._urls[index - 1]
        return self.titles[prev_url]

    def get_next(
        self,
        filepath: "TStrOrPath" = "",
        url: str = "",
    ) -> dict:
        url = url or self._get_url(filepath)
        index = self.titles[url]["index"]
        if index >= self._max_index:
            return {
                "url": "",
                "title": "",
                "section": "",
                "index": None,
            }

        next_url = self._urls[index + 1]
        return self.titles[next_url]

    def build_toc(
        self,
        nav_config: "TNavConfig",
        *,
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
        [
            ["/index", "Home", []],
            ["", "Guide", [
                ["/guide/index", "The Guide"],
                ["/guide/arguments", "The Arguments"],
                ["/guide/extra", "Extra arguments"],
            ]],
            ["/faq", "FAQ", []],
        ]

        # self.titles
        {
            "/index": {
                "url": "/index", "title": "Home", "index": 0, "section": ""
            },
            "/guide/index": {
                "url": "/guide/index", "title": "The Guide", "index": 1, "section": "Guide"
            },
            "/guide/arguments": {
                "url": "/guide/arguments", "title": "The Arguments", "index": 2, "section": "Guide"
            },
            "/guide/extra": {
                "url": "/guide/extra", "title": "Extra arguments", "index": 3, "section": "Guide"
            },
            "/faq": {
                "url": "/faq", "title": "FAQ", "index": 4, "section": ""
            },
        }
        ```
        """
        tuple_or_list = (tuple, list)

        for item in nav_config:
            if isinstance(item, str):
                title = self._extract_page_title(item)
                url = self._get_url(item)
                index = len(self.titles.keys())
                self.titles[url] = dict(
                    url=url, title=title, index=index, section=section_title
                )
                section.append([url, title, None])

            elif isinstance(item, tuple_or_list) and len(item) == 2:
                key, value = item
                if isinstance(value, str):
                    value = value.strip()
                    url = self._get_url(key)
                    index = len(self.titles.keys())
                    self.titles[url] = dict(
                        url=url,
                        title=value,
                        index=index,
                        section=section_title,
                    )
                    section.append([url, value, None])

                elif isinstance(item, tuple_or_list):
                    new_section_title = key.strip()
                    new_section = [None, new_section_title, []]
                    section.append(new_section)
                    self.build_toc(
                        nav_config=value,
                        section_title=new_section_title,
                        section=new_section[-1],
                    )

                else:
                    raise InvalidNav(item)
            else:
                raise InvalidNav(item)

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

    # Private

    def _get_url(self, filepath: "TStrOrPath") -> str:
        filepath = str(filepath).strip(" /").removesuffix(".md")
        return f"/{filepath}"

    def _extract_page_title(self, path: str) -> str:
        filepath = self._content_folder / path
        source, meta = load_markdown_metadata(filepath)
        title = meta.get("title")
        if title:
            return title

        match = rx_markdwown_h1.search(source)
        if match:
            return match.group("h1")

        match = rx_html_h1.search(source)
        if match:
            return match.group("h1")

        return filepath.name

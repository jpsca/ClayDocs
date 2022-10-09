import json
import re
from pathlib import Path
from typing import Union, Sequence

from .exceptions import InvalidNav
from .utils import load_markdown_metadata, logger


TNavConfig = Sequence[Union[str, tuple[str, str], tuple[str, "TNavConfig"]]]

rx_markdwown_h1 = re.compile(r"(^|\n)#\s+(?P<h1>[^\n]+)(\n|$)")
rx_html_h1 = re.compile(r"<h1>(?P<h1>.+)</h1>", re.IGNORECASE)


class NavTree:
    __slots__ = ("titles", "sections", "toc", "_content_folder", "_urls", "_max_index")

    def __init__(self, content_folder: Path, nav_config: "TNavConfig") -> None:
        """
        A `nav_config` looks like this:

        ```python
        [
            "filename.md",
            ("filename.md", "Custom title"),
            ...,
            (
                "Subsection title", (
                    "path/filename.md",
                    ...
                ),
            ),
        ]
        ```

        """
        self._content_folder = content_folder
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

    def get_page(self, filepath: Union[str, Path]) -> str:
        url = self._get_url(filepath)
        return url, self.titles.get(url) or {"title": "", "section": "", "index": None}

    def get_prev(self, filepath: Union[str, Path]) -> tuple[str, str]:
        url = self._get_url(filepath)
        index = self.titles[url]["index"]
        if index <= 0:
            return None, None, None

        prev_url = self._urls[index - 1]
        prev_ = self.titles[prev_url]
        prev_section = prev_["section"]
        prev_title = prev_["title"]
        return prev_section, prev_url, prev_title

    def get_next(self, filepath: Union[str, Path]) -> tuple[str, str]:
        url = self._get_url(filepath)
        index = self.titles[url]["index"]
        if index >= self._max_index:
            return None, None, None

        next_url = self._urls[index + 1]
        next_ = self.titles[next_url]
        next_section = next_["section"]
        next_title = next_["title"]
        return next_section, next_url, next_title

    def build_toc(
        self,
        nav_config: "TNavConfig",
        *,
        section_title: str = "",
        section: list,
    ) -> None:
        tuple_or_list = (tuple, list)

        for item in nav_config:
            if isinstance(item, str):
                title = self._extract_page_title(item)
                url = self._get_url(item)
                index = len(self.titles.keys())
                self.titles[url] = dict(title=title, index=index, section=section_title)
                section.append([url, title])

            elif isinstance(item, tuple_or_list) and len(item) == 2:
                key, value = item
                if isinstance(value, str):
                    value = value.strip()
                    url = self._get_url(key)
                    index = len(self.titles.keys())
                    self.titles[url] = dict(title=value, index=index, section=section_title)
                    section.append([url, value])

                elif isinstance(item, tuple_or_list):
                    new_section_title = key.strip()
                    new_section = [new_section_title, []]
                    section.append(new_section)
                    self.build_toc(
                        nav_config=value,
                        section_title=new_section_title,
                        section=new_section[1],
                    )

                else:
                    raise InvalidNav(item)
            else:
                raise InvalidNav(item)

    def _get_url(self, filepath: Union[str, Path]) -> str:
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

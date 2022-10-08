import json
import re
from pathlib import Path
from typing import Union, Sequence

from .exceptions import InvalidNav
from .utils import load_markdown_metadata, logger


TNavConfig = Sequence[Union[str, tuple[str, str], tuple[str, "TNavConfig"]]]

rx_markdwown_h1 = re.compile(r"(^|\n)#\s*(?P<h1>[^\n]+)(\n|$)")
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
        self.set_titles(nav_config)
        self.set_toc()
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

        prev_ = self.title[prev_url]
        prev_section = self.sections[prev_["section"]]
        prev_url = self._urls[index - 1]
        prev_title = prev_["title"]
        return prev_section, prev_url, prev_title

    def get_next(self, filepath: Union[str, Path]) -> tuple[str, str]:
        url = self._get_url(filepath)
        index = self.titles[url]["index"]
        if index >= self._max_index:
            return None, None, None

        next_ = self.title[next_url]
        next_section = self.sections[next_["section"]]
        next_url = self._urls[index + 1]
        next_title = next_["title"]
        return next_section, next_url, next_title

    def set_titles(
        self,
        nav_config: "TNavConfig",
        *,
        index: int = 0,
        section: int = 0,
    ) -> dict[str, tuple[int, str]]:
        for item in nav_config:
            if isinstance(item, str):
                title = self._extract_page_title(item)
                if not self.sections:
                    self.sections.append("")
                self._set_title(item, title=title, index=index, section=section)

            elif isinstance(item, tuple) and len(item) == 2:
                key, value = item
                if isinstance(value, str):
                    if not self.sections:
                        self.sections.append("")
                    self._set_title(key, title=value, index=index, section=section)

                elif isinstance(item, tuple):
                    self.sections.append(key.strip())
                    self.set_titles(
                        nav_config=value,
                        index=index,
                        section=section + 1,
                    )

                else:
                    raise InvalidNav(item)
            else:
                raise InvalidNav(item)

            index += 1

    def set_toc(self) -> None:
        sections = {}
        for url, data in self.titles.items():
            sectitle = self.sections[data["section"]]
            sections.setdefault(sectitle, [])
            sections[sectitle].append((url, data["title"]))

        self.toc = tuple((title, tuple(pages)) for title, pages in sections.items())

    def _get_url(self, filepath: Union[str, Path]) -> str:
        filepath = str(filepath).strip(" /").removesuffix(".md")
        return f"/{filepath}"

    def _set_title(self, filepath: Path, **data) -> None:
        url = self._get_url(filepath)
        self.titles[url] = data

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

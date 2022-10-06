from pathlib import Path
from typing import Union, Sequence

from .exceptions import InvalidNav
from .utils import load_markdown_metadata


TNavConfig = Sequence[Union[str, tuple[str, str], tuple[str, "TNavConfig"]]]


class NavTree:
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
        self.titles = get_titles({}, content_folder, nav_config)
        self.files = list(self.titles.keys())
        self.max_index = len(self.files) - 1

    def get_title(self, filename):
        return self.titles[filename][1]

    def get_prev(self, filename):
        index = self.titles[filename][0]
        if index <= 0:
            return None, None
        prev_filename = self.files[index - 1]
        prev_title = self.title[prev_filename]
        return prev_title, prev_filename

    def get_next(self, filename):
        index = self.titles[filename][0]
        if index >= self.max_index:
            return None, None
        next_filename = self.files[index + 1]
        next_title = self.title[next_filename]
        return next_title, next_filename


def get_titles(
    titles: "dict[str, tuple[int, str]]",
    content_folder: Path,
    nav_config: "TNavConfig",
    index: int = 0,
) -> "dict[str, tuple[int, str]]":
    for item in nav_config:
        if isinstance(item, str):
            filepath = content_folder / item
            title = get_title(filepath)
            titles[item] = (index, title)

        elif isinstance(item, tuple) and len(item) == 2:
            key, value = item
            if isinstance(value, str):
                titles[key] = (index, value)

            elif isinstance(item, tuple):
                get_titles(titles, content_folder, nav_config=value)

            else:
                raise InvalidNav(item)
        else:
            raise InvalidNav(item)

        index += 1
    return titles


def get_title(filepath: Path) -> str:
    _source, meta = load_markdown_metadata(filepath)
    title = meta.get("title")
    if not title:
        title = filepath.name
    return title

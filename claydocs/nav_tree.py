"""
nav_config example:

[
    { "Home": "index.md" },
    "faq.md",
    {
        "Guide": [
            "guide/index.md",
            "guide/attributes.md",
            "guide/extra.md",
            "guide/css_and_js.md",
        ]
    }
"""
from pathlib import Path
from typing import Union

from .extra import load_markdown_metadata
from .exceptions import InvalidNav


TNavConfig = list[Union[str, dict[str, str], dict[str, "TNavConfig"]]]


class NavTree:
    def __init__(self, content_folder: Path, nav_config: "TNavConfig") -> None:
        nav = {}


def get_titles(
    content_folder: Path,
    nav_config: "TNavConfig",
    titles: "dict[str, dict[str, Union[str, int]]]",
    curr_index: int = 0,
) -> None:
    for item in nav_config:
        if isinstance(item, str):
            meta, _ = load_markdown_metadata(content_folder, item)
            title = meta.get("title", item)
            curr_index += 1
            titles[item] = {"index": curr_index, "title": title}
        elif isinstance(item, dict):
            pass
        else:

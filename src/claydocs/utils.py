import logging
import random
import re
import time
import typing as t
from dataclasses import dataclass, field

import jinjax  # noqa
import yaml

from .exceptions import InvalidFrontMatter

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: no cover
    from yaml import SafeLoader  # type: ignore

if t.TYPE_CHECKING:
    from pathlib import Path
    from jinjax.catalog import Catalog
    from .nav import Nav
    from .server import LiveReloadServer


LOGGER_NAME = "claydocs"
LOGGER_LEVEL = logging.INFO

META_START = "---"
META_END = "\n---"

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(LOGGER_LEVEL)


class THasPaths:
    STATIC_FOLDER: str
    THEME_FOLDER: str
    BUILD_FOLDER: str
    CACHE_FOLDER: str

    STATIC_URL: str
    THUMBNAILS_URL: str
    DEFAULT_COMPONENT: str

    root: "Path"
    content_folder: "Path"
    static_folder: "Path"
    build_folder: "Path"
    build_folder_static: "Path"
    cache_folder: "Path"
    temp_folder: "Path"
    static_url: str
    add_ons: list[t.Any]
    nav: "Nav"
    server: "LiveReloadServer"


class THasRender(THasPaths):
    catalog: "Catalog"

    def render_page(self, page: "Page", **kw) -> str:  # type: ignore
        ...

    def get_cached_page(self, url: str, **kw) -> str:  # type: ignore
        ...

    def refresh(self, event) -> None:
        ...


@dataclass
class Page:
    lang: str = ""
    url: str = ""
    filename: str = ""
    title: str = ""
    index: int = 0
    section: str = ""
    meta: dict = field(default_factory=dict)
    html: str = ""
    cache_path: "Path | None" = None


def is_debug():
    return logger.level == logging.DEBUG


def timestamp() -> int:
    return round(time.monotonic() * 1000)


def load_markdown_metadata(filepath: "Path") -> tuple[str, dict]:
    source = filepath.read_text().lstrip()
    if not source.startswith(META_START):
        return source, {}

    source = source.lstrip("-")
    front_matter, source = source.split(META_END, 1)
    try:
        meta = yaml.load(front_matter, SafeLoader)
    except Exception as err:
        raise InvalidFrontMatter(str(filepath), *err.args)

    return source.lstrip(" -"), meta


RANDOM_MESSAGES = [
    "Distilling enjoyment",
    "Adding emotional depth",
    "Filtering the ozone",
    "Testing for perfection",
    "Stretching the truth",
    "Optimizing for happiness",
    "Swapping time and space",
    "Reversing the bits polarity",
    "Extracting meaning",
    "Counting to 42 backwards",
]


def print_random_messages(num=3) -> None:
    for message in random.sample(RANDOM_MESSAGES, num):
        logger.info(f"{message}...")


rx_widont = re.compile(r"\s+(\S+\s*)$")


def widont(value):
    """
    Adds an HTML non-breaking space between the final two words of the string to
    avoid "widowed" words.

    Examples:

    >>> widont('Test   me   out')
    'Test   me&nbsp;out'

    >>> widont('It works with trailing spaces too  ')
    'It works with trailing spaces&nbsp;too  '

    >>> widont('no-effect')
    'no-effect'

    """

    def replace(matchobj):
        return f"&nbsp;{matchobj.group(1)}"

    return rx_widont.sub(replace, str(value))

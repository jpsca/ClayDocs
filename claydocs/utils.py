import logging
import random
import re
import typing as t
from fnmatch import fnmatch

import yaml

from .exceptions import InvalidFrontMatter

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: no cover
    from yaml import SafeLoader  # type: ignore

if t.TYPE_CHECKING:
    from pathlib import Path
    from tcom.catalog import Catalog
    from .nav import Nav


LOGGER_LEVEL = logging.INFO
LOGGER_NAME = "claydocs"
META_START = "---"
META_END = "\n---"

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(LOGGER_LEVEL)
ch = logging.StreamHandler()
ch.setLevel(LOGGER_LEVEL)

formatter = logging.Formatter(
    fmt="{levelname: <10}-  [{asctime}] {message}",
    style="{",
    datefmt="%H:%M:%S",
)
ch.setFormatter(formatter)
logger.addHandler(ch)


class THasPaths:
    THEME_FOLDER: str
    COMPONENTS_FOLDER: str
    CONTENT_FOLDER: str
    STATIC_FOLDER: str
    BUILD_FOLDER: str
    STATIC_URL: str
    DEFAULT_COMPONENT: str

    theme_folder: "Path"
    components_folder: "Path"
    content_folder: "Path"
    static_folder: "Path"
    build_folder: "Path"

    nav: "Nav"


class THasRender(THasPaths):
    catalog: "Catalog"

    def render(self, name: str, **kw) -> str:  # type: ignore
        ...


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


def current_path(
    path,
    *url_patterns,
    partial: bool = False,
    classes: str = "active",
) -> str:
    curr_path = re.sub("index.html$", "", path).strip("/")
    for urlp in url_patterns:
        urlp = re.sub("index.html$", "", urlp.strip("/")).strip("/")
        if fnmatch(curr_path, urlp) or (partial and curr_path.startswith(urlp)):
            return classes
    return ""


def is_(func: t.Callable) -> t.Callable:
    def test_is(*args, **kw):
        return bool(func(*args, **kw))

    return test_is


RANDOM_MESSAGES = [
    "Distilling enjoyment",
    "Adding emotional depth",
    "Filtering the ozone",
    "Testing for perfection",
    "Stretching the truth",
    "Optimizing for happiness",
    "Swapping time and space",
    "Reversing the polarity",
    "Self-affirming",
    "Extracting meaning",
]


def print_random_messages(num=2) -> None:
    for message in random.sample(RANDOM_MESSAGES, num):
        logger.info(f"{message}...")

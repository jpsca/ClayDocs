import logging
import random
import time
import typing as t

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


LOGGER_NAME = "claydocs"
LOGGER_LEVEL = logging.INFO

META_START = "---"
META_END = "\n---"

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(LOGGER_LEVEL)


class THasPaths:
    THEME_FOLDER: str
    COMPONENTS_FOLDER: str
    CONTENT_FOLDER: str
    STATIC_FOLDER: str
    BUILD_FOLDER: str

    STATIC_URL: str
    THUMBNAILS_URL: str
    DEFAULT_COMPONENT: str

    theme_folder: "Path"
    components_folder: "Path"
    content_folder: "Path"
    static_folder: "Path"
    build_folder: "Path"
    temp_folder: "Path"

    nav: "Nav"


class THasRender(THasPaths):
    catalog: "Catalog"

    def render(self, name: str, **kw) -> str:  # type: ignore
        ...


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
    "Reversing the polarity",
    "Self-affirming",
    "Extracting meaning",
]


def print_random_messages(num=3) -> None:
    for message in random.sample(RANDOM_MESSAGES, num):
        logger.info(f"{message}...")

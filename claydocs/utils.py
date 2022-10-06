import logging
import re
import textwrap
from fnmatch import fnmatch
from typing import Any

import tomlkit
import pygments
from markupsafe import Markup
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from .exceptions import InvalidFrontMatter


LOGGER_NAME = "claydocs"
FRONT_MATTER_SEP = "---"

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    fmt="{levelname: <10}-  [{asctime}] {message}",
    style="{",
    datefmt="%H:%M:%S",
)
ch.setFormatter(formatter)
logger.addHandler(ch)


def current_path(path, *url_patterns, partial=False, classes="active"):
    curr_path = re.sub("index.html$", "", path).strip("/")
    for urlp in url_patterns:
        urlp = re.sub("index.html$", "", urlp.strip("/")).strip("/")
        if fnmatch(curr_path, urlp) or (partial and curr_path.startswith(urlp)):
            return classes
    return ""


def load_markdown_metadata(source: str, filename: str) -> "dict[str, Any]":
    if not source.startswith(FRONT_MATTER_SEP):
        return {}, source
    source = source.removeprefix(FRONT_MATTER_SEP)
    front_matter, source = source.split(FRONT_MATTER_SEP, 1)
    front_matter = (
        front_matter
        .strip()
        .replace(" False\n", " false\n")
        .replace(" True\n", " true\n")
    )
    try:
        return tomlkit.parse(front_matter), source.strip()
    except tomlkit.exceptions.TOMLKitError as err:
        raise InvalidFrontMatter(filename, *err.args)


def highlight(
        source,
        language="",
        *,
        linenos=True,
        **options
    ):
    source = textwrap.dedent(source.strip("\n"))
    lexer = None
    if language:
        lexer = get_lexer_by_name(language, stripall=True)

    options.setdefault("wrapcode", True)
    formatter = HtmlFormatter(
        linenos="inline" if linenos else False,
        **options,
    )
    html = pygments.highlight(source, lexer=lexer, formatter=formatter)
    html = html.replace("{", "&lbrace;")
    print("="*20, "\n", html)
    return Markup(html)

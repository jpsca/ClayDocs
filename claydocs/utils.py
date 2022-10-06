import logging
import re
import textwrap
from fnmatch import fnmatch
from pathlib import Path

import pygments
import yaml
from markupsafe import Markup
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from .exceptions import InvalidFrontMatter

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: no cover
    from yaml import SafeLoader  # type: ignore


LOGGER_NAME = "claydocs"
META_START = "---"
META_END = "\n---"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    fmt="{levelname: <10}-  [{asctime}] {message}",
    style="{",
    datefmt="%H:%M:%S",
)
ch.setFormatter(formatter)
logger.addHandler(ch)


def load_markdown_metadata(filepath: Path) -> tuple[str, dict]:
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


def current_path(path, *url_patterns, partial=False, classes="active"):
    curr_path = re.sub("index.html$", "", path).strip("/")
    for urlp in url_patterns:
        urlp = re.sub("index.html$", "", urlp.strip("/")).strip("/")
        if fnmatch(curr_path, urlp) or (partial and curr_path.startswith(urlp)):
            return classes
    return ""


def highlight(source, language="", *, linenos=True, **options):
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
    print("=" * 20, "\n", html)
    return Markup(html)

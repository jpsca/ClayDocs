import re
from fnmatch import fnmatch

import tomlkit

from .exceptions import InvalidFrontMatter


FRONT_MATTER_SEP = "---"


def current_path(path, *url_patterns, partial=False, classes="active"):
    curr_path = re.sub("index.html$", "", path).strip("/")
    for urlp in url_patterns:
        urlp = re.sub("index.html$", "", urlp.strip("/")).strip("/")
        if fnmatch(curr_path, urlp) or (partial and curr_path.startswith(urlp)):
            return classes
    return ""


def load_markdown_metadata(source: str, filename: str) -> "dict[str, t.Any]":
    if not source.startswith(FRONT_MATTER_SEP):
        return {}
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

import re
from fnmatch import fnmatch


def current_path(path, *url_patterns, partial=False, classes="active"):
    curr_path = re.sub("index.html$", "", path).strip("/")
    for urlp in url_patterns:
        urlp = re.sub("index.html$", "", urlp.strip("/")).strip("/")
        if fnmatch(curr_path, urlp) or (partial and curr_path.startswith(urlp)):
            return classes
    return ""

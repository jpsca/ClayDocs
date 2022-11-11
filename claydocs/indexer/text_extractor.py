import re
from html.parser import HTMLParser


START_PAGE = "startpage"
END_PAGE = "endpage"
HEADER_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")
IGNORE_TAGS = ("a", "span", "hr")
NON_DATA_TAGS = ("script", "style", "svg", "iframe", "form")
PRE_TAG = "pre"
ID_ATTR = "id"
DETAILS_TAG = "details"

rx_spaces = re.compile(r"[\n\s]+")


class TextExtractor(HTMLParser):
    sections: list[dict[str, str]]

    _capture: bool = True
    _in_page: bool = False
    _in_pre: bool = False
    _in_header: bool = False

    _loc: str
    _title: list[str]
    _body: list[str]

    def __init__(self, title: str = ""):
        super().__init__()
        self.sections = []
        self._loc = ""
        self._title = [title]
        self._body = []

    def handle_starttag(self, tag: str, attrs: list):
        html_attrs = ""

        if tag in NON_DATA_TAGS:
            self._capture = False
            return

        if not (self._in_page and self._capture):
            return

        if tag in IGNORE_TAGS:
            return

        if tag in HEADER_TAGS:
            attr_id = next((x for x in attrs if x[0] == ID_ATTR), None)
            if attr_id:
                self.save_section()
                self._loc = f"#{attr_id[1]}"
                self._title = []
                self._body = []
                self._in_header = True
                return

        if self._in_header:
            return

        if tag == PRE_TAG:
            self._in_pre = True

        if tag == DETAILS_TAG:
            html_attrs = " open"

        self._body.append(f"<{tag}{html_attrs}>")

    def handle_endtag(self, tag: str):
        if tag in NON_DATA_TAGS:
            self._capture = True
            return

        if not (self._in_page and self._capture):
            return

        if tag in IGNORE_TAGS:
            return

        if tag in HEADER_TAGS:
            self._in_header = False
            return

        if self._in_header:
            return

        if tag == PRE_TAG:
            self._in_pre = False

        self._body.append(f"</{tag}>")

    def handle_comment(self, data: str):
        if data == START_PAGE:
            self._in_page = True
        elif data == END_PAGE:
            self._in_page = False

    def handle_data(self, data: str):
        if not (self._in_page and self._capture):
            return

        if self._in_pre:
            self._body.append(data)
            return

        data = data.replace("¶", "")
        data = rx_spaces.sub(" ", data).lstrip()

        if self._in_header:
            self._title.append(data.strip())
            return

        self._body.append(data)

    def handle_entityref(self, name):
        self.handle_data(f"&{name};")

    def handle_charref(self, name):
        self.handle_data(f"&#{name};")

    def save_section(self):
        body = "".join(self._body).strip()
        self.sections.append({
            "loc": self._loc,
            "title": "".join(self._title),
            "body": body,
        })

    def close(self):
        self.save_section()
        super().close()


def extract_sections(html: str, loc: str, title: str) -> list[dict[str, str]]:
    parser = TextExtractor(title=title)
    parser.feed(html)
    parser.close()
    sections = [
        {
            "loc": f"{loc}{sec['loc']}",
            "title": sec["title"],
            "body": sec["body"],
        }
        for sec in parser.sections
    ]
    return sections

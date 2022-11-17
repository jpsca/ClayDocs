import html
import re
from html.parser import HTMLParser


TSections = dict[str, dict[str, str]]

START_PAGE = "startpage"
END_PAGE = "endpage"

# Ignore these tags but save its content
IGNORE_TAGS = (
    "a",
    "address",
    "article",
    "aside",
    "div",
    "fieldset",
    "figcaption>",
    "footer",
    "header",
    "hgroup",
    "hr",
    "main",
    "section",
    "span",
    "srcset",
    "summary",
    "tbody",
    "thead",
)

# Ignore these tags and its content
IGNORE_TAG_AND_CONTENTS = (
    "button",
    "dialog",
    "form",
    "iframe",
    "input",
    "nav",
    "script",
    "select",
    "style",
    "svg",
    "template",
    "textarea",
    "video",
)

HEADER_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")
PRE_TAG = "pre"
DETAILS_TAG = "details"

CUT_ON = (
    "address",
    "article",
    "aside",
    "blockquote",
    DETAILS_TAG,
    "div",
    "dl",
    "figure",
    "footer",
    "header",
    *HEADER_TAGS,
    "ol",
    "p",
    PRE_TAG,
    "section",
    "table",
    "ul",
)
ID_ATTR = "id"

rx_multiple_spaces = re.compile(r"\s+")


class TextExtractor(HTMLParser):
    sections: TSections

    _capture: bool = True
    _in_page: bool = False
    _in_pre: bool = False
    _in_header: bool = False

    _page_title: str
    _base_loc: str

    _loc: str
    _title: list[str]
    _body: list[str]
    _uid: int

    def __init__(self, page_title: str = "", base_loc: str = ""):
        super().__init__()
        self.sections = {}
        self._page_title = page_title
        self._base_loc = base_loc
        self._loc = ""
        self._title = []
        self._body = []
        self._uid = 1

    def handle_starttag(self, tag: str, attrs: list):
        if not (self._in_page and self._capture):
            return

        if tag in IGNORE_TAG_AND_CONTENTS:
            self._capture = False
            return

        if self._in_pre:
            if tag not in IGNORE_TAGS:
                self._body.append(f"<{tag}>")
            return

        if self._in_header:
            return

        if tag in CUT_ON:
            self.save_section()

        if tag in HEADER_TAGS:
            attr_id = next((x for x in attrs if x[0] == ID_ATTR), None)
            self._title = []
            self._body = []
            if attr_id:
                self._loc = attr_id[1]
                self._in_header = True
            return

        if tag == PRE_TAG:
            self._in_pre = True

        if tag not in IGNORE_TAGS:
            self._body.append(f"<{tag}>")

    def handle_endtag(self, tag: str):
        if not (self._in_page and self._capture):
            return

        if tag in IGNORE_TAG_AND_CONTENTS:
            self._capture = True
            return

        if tag == PRE_TAG:
            self._in_pre = False

        if self._in_pre:
            if tag not in IGNORE_TAGS:
                self._body.append(f"</{tag}>")
            return

        if tag in HEADER_TAGS:
            self._in_header = False
            return

        if self._in_header:
            return

        if tag not in IGNORE_TAGS:
            self._body.append(f"</{tag}>")

    def handle_comment(self, data: str):
        if data == START_PAGE:
            self._in_page = True
        elif data == END_PAGE:
            self._in_page = False

    def handle_data(self, data: str):
        if not (self._in_page and self._capture):
            return

        data = html.escape(data.replace("¶", ""))

        if self._in_pre:
            self._body.append(data)
            return

        data = rx_multiple_spaces.sub(" ", data)

        if self._in_header:
            self._title.append(data)
            return

        self._body.append(data)

    def handle_entityref(self, name):
        self.handle_data(f"&{name};")

    def handle_charref(self, name):
        self.handle_data(f"&#{name};")

    def save_section(self):
        title = "".join(self._title).strip()
        if not title or title == self._page_title:
            title = self._page_title
            parent = ""
        else:
            parent = self._page_title

        num_parts = len(self._body)
        body = "".join(self._body).strip()
        self._body = []

        if not body or body == title:
            return

        if num_parts == 1 and body.startswith("<"):
            return

        loc = f"{self._base_loc}#{self._loc}"

        self.sections[str(self._uid)] = {
            "parent": parent,
            "title": title,
            "body": body,
            "loc": loc
        }
        self._uid += 1

    def close(self):
        self.save_section()
        super().close()


def extract_sections(html: str, loc: str, title: str) -> TSections:
    parser = TextExtractor(page_title=title, base_loc=loc)
    parser.feed(html)
    parser.close()
    return parser.sections

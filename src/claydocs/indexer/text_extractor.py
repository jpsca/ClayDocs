import html
import re
from html.parser import HTMLParser


TDoc = dict[str, str]

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

TO_DIV_TAGS = ("details",)

HEADER_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")
PRE_TAG = "pre"
CODE_TAG = "code"

CUT_ON = (
    "address",
    "article",
    "aside",
    "blockquote",
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
rx_non_text = re.compile(
    r"[^\w./_\-]|\s[._-]+|[._-]+\s|[._-]+$|^[._-]+|\s/\s", re.UNICODE | re.IGNORECASE
)


def make_doc(
    *,
    id: str,
    title: str,
    body: str = "",
    raw: str = "",
    parent: str = "",
    loc: str = "",
) -> TDoc:
    return {
        "id": id,
        "title": title,
        "body": body,
        "raw": raw,
        "parent": parent,
        "loc": loc,
    }


class TextExtractor(HTMLParser):
    docs: list[TDoc]

    _capture: bool = True
    _in_page: bool = False
    _in_pre: bool = False
    _in_code: bool = False
    _in_header: bool = False

    _page_title: str
    _base_loc: str

    _loc: str
    _title: list[str]
    _body: list[str]
    _raw: list[str]
    _id: int

    def __init__(self, page_title: str = "", base_loc: str = ""):
        super().__init__()
        self.docs = []
        self._page_title = page_title
        self._base_loc = base_loc
        self._loc = ""
        self._title = []
        self._body = []
        self._raw = []
        self._id = 1

    def handle_starttag(self, tag: str, attrs: list):
        if not (self._in_page and self._capture):
            return

        if tag in IGNORE_TAG_AND_CONTENTS:
            self._capture = False
            return

        if self._in_header:
            return

        if tag in CUT_ON:
            self.save_section()

        if tag in IGNORE_TAGS:
            return

        if tag in HEADER_TAGS:
            attr_id = next((x for x in attrs if x[0] == ID_ATTR), None)
            self._title = []
            if attr_id:
                self._loc = attr_id[1]
                self._in_header = True
            return

        if tag == PRE_TAG:
            self._in_pre = True

        if tag == CODE_TAG:
            self._in_code = True

        if tag in TO_DIV_TAGS:
            tag = "div"

        self._body.append(f"<{tag}>")

    def handle_endtag(self, tag: str):
        if not (self._in_page and self._capture):
            return

        if tag in IGNORE_TAG_AND_CONTENTS:
            self._capture = True
            return

        if tag in IGNORE_TAGS:
            return

        if tag in HEADER_TAGS:
            self._in_header = False
            return

        if tag == PRE_TAG:
            self._in_pre = False

        if tag == CODE_TAG:
            self._in_code = False

        if tag in TO_DIV_TAGS:
            tag = "div"

        self._body.append(f"</{tag}>")

    def handle_comment(self, data: str):
        if data == START_PAGE:
            self._in_page = True
        elif data == END_PAGE:
            self._in_page = False

    def handle_data(self, data: str):
        if not (self._in_page and self._capture):
            return

        text_data = data
        data = html.escape(text_data)

        if self._in_header:
            self._title.append(data)
            return

        if not self._in_pre:
            data = rx_multiple_spaces.sub(" ", data)

        if not self._in_code:
            text_data = rx_non_text.sub(" ", text_data)

        self._raw.append(text_data)
        self._body.append(data)

    def handle_entityref(self, name):
        self.handle_data(f"&{name};")

    def handle_charref(self, name):
        self.handle_data(f"&#{name};")

    def save_section(self):
        raw = "".join(self._raw).strip()
        raw = rx_multiple_spaces.sub(" ", raw)
        if not raw:
            return

        title = "".join(self._title).strip()
        title = rx_multiple_spaces.sub(" ", title)
        body = "".join(self._body).strip()

        if not title or title == self._page_title:
            title = self._page_title
            parent = ""
        else:
            parent = self._page_title

        self._body = []
        self._raw = []

        if title == body:
            return

        loc = f"{self._base_loc}#{self._loc}"
        self.docs.append(
            make_doc(
                id=str(self._id),
                parent=parent,
                title=title,
                body=body,
                raw=raw,
                loc=loc,
            )
        )
        self._id += 1

    def close(self):
        self.save_section()
        super().close()


def extract_docs(html: str, loc: str, title: str) -> list[TDoc]:
    parser = TextExtractor(page_title=title, base_loc=loc)
    parser.feed(html)
    parser.close()
    return parser.docs

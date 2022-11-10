import re
from html.parser import HTMLParser


START_PAGE = "startpage"
END_PAGE = "endpage"

NON_DATA_TAGS = ("script", "style", "svg", "iframe", "form")
BLOCK_TAGS = (
    "address", "article", "aside", "blockquote", "dd", "details",
    "dialog", "div", "dl", "dt", "fieldset", "figcaption", "figure",
    "footer", "h1", "h2", "h3", "h4", "h5", "h6", "header",
    "hgroup", "hr", "li", "main", "nav", "ol", "p", "pre", "section",
    "table", "ul",
)

rx_line_jumps = re.compile(r"\n\n+")
rx_spaces = re.compile(r"\s\s+")


class TextExtractor(HTMLParser):
    _capture: bool = True
    _page: bool = False
    _text: list[str]

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._text = []

    def handle_starttag(self, tag: str, attrs: list):
        if tag in NON_DATA_TAGS:
            self._capture = False
        elif tag in BLOCK_TAGS:
          self._text.append("\n")

    def handle_endtag(self, tag: str):
        if tag in NON_DATA_TAGS:
            self._capture = True
        elif tag in BLOCK_TAGS:
          self._text.append("\n")

    def handle_comment(self, data: str):
        if data == START_PAGE:
            self._page = True
        elif data == END_PAGE:
            self._page = False

    def handle_data(self, data: str):
        if self._page and self._capture:
            data = data.replace("¶" ,"")
            self._text.append(data)

    def unknown_decl(self, data: str):
        if self._page and self._capture:
            self._text.append(data)

    def text(self):
        text = "".join(self._text)
        text = rx_line_jumps.sub("\n", text)
        text = rx_spaces.sub(" ", text)
        return text.strip()




def extract_text(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    parser.close()
    text = parser.text()
    print("="*20)
    print(text)
    return text

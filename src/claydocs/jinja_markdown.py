
import textwrap
import typing as t

from jinja2 import nodes
from jinja2.ext import Extension

if t.TYPE_CHECKING:
    from jinja2 import Environment
    from jinja2.nodes import Node
    from jinja2.parser import Parser


class MarkdownExtension(Extension):
    tags = set(["markdown"])

    def __init__(self, environment: "Environment") -> None:
        super(MarkdownExtension, self).__init__(environment)

    def parse(self, parser: "Parser") -> t.Union["Node", t.List["Node"]]:
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(("name:endmarkdown", ), drop_needle=True)
        call_node = self.call_method("_render_markdown", [], [])
        return nodes.CallBlock(call_node, [], [], body).set_lineno(lineno)

    def _dedent(self, text: str) -> str:
        return textwrap.dedent(text.strip("\n"))

    def _render_markdown(self, caller: "t.Callable | None") -> str:
        if not caller:
            return ""
        body = self._dedent(caller() or "")
        return self.environment.markdowner.convert(body)  # type: ignore

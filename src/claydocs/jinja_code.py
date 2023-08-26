"""
NOTE: Convert this to a separated Python library when you have time
"""
import textwrap
import typing as t

from jinja2 import nodes
from jinja2.ext import Extension

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter

if t.TYPE_CHECKING:
    from jinja2.nodes import Node
    from jinja2.parser import Parser


class CodeExtension(Extension):
    """Highlight code blocks using Pygments.

    Example:

    ```html+jinja
    <div>
        {% code "python" %}
        from foo import Bar

        bar = Bar()
        bar.open()
        {% endcode %}
    </div>
    ```

    Other Pygments args like, `lineno` can be passed as well, even if the language
    is not specified.

    The whole block of code can be indented without causing problems, just
    make sure the fire the first line of code has the "base" indentation,
    meaning the indentation the rest of the code ahould considers as "not indented"
    """

    tags = set(["code"])

    def parse(self, parser: "Parser") -> "Node":
        lineno = parser.stream.current.lineno
        # the first token is the token that started the tag.
        parser.stream.skip(1)
        args, kwargs = self._parse_args(parser)

        body = parser.parse_statements(("name:endcode",), drop_needle=True)
        call_node = self.call_method("_render_code", args, kwargs)
        return nodes.CallBlock(call_node, [], [], body).set_lineno(lineno)

    def _parse_args(self, parser: "Parser") -> tuple[list, list]:
        args = []
        kwargs = []
        require_comma = False

        while parser.stream.current.type != "block_end":
            if require_comma:
                parser.stream.expect("comma")
                if parser.stream.current.type == "block_end":
                    break

            if (
                parser.stream.current.type == "name"
                and parser.stream.look().type == "assign"
            ):
                key = parser.stream.current.value
                parser.stream.skip(2)
                value = parser.parse_expression()
                kwargs.append(nodes.Keyword(key, value, lineno=value.lineno))
            else:
                if kwargs:
                    parser.fail("Invalid argument syntax", parser.stream.current.lineno)
                args.append(parser.parse_expression())

            require_comma = True

        return args, kwargs

    def _dedent(self, text: str) -> str:
        return textwrap.dedent(text.strip("\n"))

    def _render_code(
        self,
        lang: "str | None" = None,
        *,
        caller: "t.Callable | None" = None,
        **kwargs,
    ) -> str:
        if not caller:
            return ""

        body = self._dedent(caller() or "")

        if lang is None:
            lexer = guess_lexer(body)
        else:
            lexer = get_lexer_by_name(lang, stripall=False)

        formatter = HtmlFormatter(**kwargs)

        return highlight(body, lexer, formatter) or ""

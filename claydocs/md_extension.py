import textwrap
import typing as t

import markdown
from jinja2_simple_tags import ContainerTag

if t.TYPE_CHECKING:
    from jinja2 import Environment


__all__ = ["DEFAULT_EXTENSIONS", "MarkdownExtension"]

DEFAULT_EXTENSIONS = [
    "attr_list",
    "sane_lists",
    "smarty",
    "tables",
    "pymdownx.betterem",
    "pymdownx.caret",
    "pymdownx.critic",
    "pymdownx.emoji",
    "pymdownx.keys",
    "pymdownx.magiclink",
    "pymdownx.mark",
    "pymdownx.saneheaders",
    "pymdownx.smartsymbols",
    "pymdownx.tasklist",
    "pymdownx.tilde",
]


class MarkdownExtension(ContainerTag):
    tags = {"markdown"}

    def __init__(self, environment: "Environment", extensions: "list[str]" = DEFAULT_EXTENSIONS) -> None:
        super().__init__(environment)
        self.markdowner = markdown.Markdown(extensions=extensions)
        environment.extend(markdowner=self.markdowner)

    def render(self, caller: "t.Optional[t.Callable]" = None) -> str:
        text = caller() if caller else ""
        text = textwrap.dedent(text.strip("\n"))
        return self.markdowner.convert(text)

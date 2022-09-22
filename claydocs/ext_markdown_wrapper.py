import typing as t

from jinja2.ext import Extension
from tcom.html_attrs import HTMLAttrs

from .extra import load_markdown_metadata


MARKDOWN_EXTENSION = ".md"
DEFAULT_COMPONENT = "Page"
WRAPPER = "<{component} {attrs}>{source}</{component}>"


class MarkdownWrapperExtension(Extension):
    def preprocess(
        self,
        source: str,
        name: "t.Optional[str]" = None,
        filename: "t.Optional[str]" = None,
    ) -> str:
        """If the template is a Markdown file, extracts the metadata from the front matter
        and adds a parent component"""
        if not name or not name.endswith(MARKDOWN_EXTENSION):
            return source
        return self._wrap_in_component(source, name, filename)

    def _wrap_in_component(
        self,
        source: str,
        name: "t.Optional[str]" = None,
        filename: "t.Optional[str]" = None,
    ) -> str:
        meta, source = load_markdown_metadata(source, filename)
        meta.setdefault("title", name or '')
        component = meta.pop("component", DEFAULT_COMPONENT)
        html_attrs = HTMLAttrs(meta)
        return WRAPPER.format(
            component=component,
            attrs=html_attrs.render(),
            source=source,
        )

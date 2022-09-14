import typing as t

from jinja2_simple_tags import ContainerTag
from pymdownx.highlight import Highlight


class HighlightExtension(ContainerTag):
    tags = {"highlight"}

    def render(
        self,
        language,
        linenums=True,
        linenums_style="pymdownx-inline",
        line_spans="",
        anchor_linenums=False,
        line_anchors="",
        css_class='highlight',
        inline=False,
        hl_lines=None,
        linestart=-1,
        linestep=-1,
        linespecial=-1,
        classes=None,
        id_value='',
        attrs=None,
        title=None,
        caller: "t.Optional[t.Callable]" = None
    ) -> str:
        self.code_block_count += 1
        source = caller().strip() if caller else ""

        Highlight(
            linenums=linenums,
            linenums_style=linenums_style,
            line_spans=line_spans,
            anchor_linenums=anchor_linenums,
            line_anchors=line_anchors,
        ).highlight(
            source,
            language=language,
            css_class=css_class,
            inline=inline,
            hl_lines=hl_lines,
            linestart=linestart,
            linestep=linestep,
            linespecial=linespecial,
            classes=classes,
            id_value=id_value,
            attrs=attrs,
            title=title,
            code_block_count=self.code_block_count
        )

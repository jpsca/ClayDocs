import re
import typing as t

from lunr import lunr

from ..utils import logger
from .builder import Builder
from .text_extractor import TSections, extract_sections, rx_multiple_spaces


if t.TYPE_CHECKING:
    from ..nav import Page


rx_html_tags = re.compile(r"</?[a-z]+[1-6]?( open)?>")


class Indexer:
    def __init__(self, render: t.Callable) -> None:
        self.render = render

    def index(self, pages: "list[Page]") -> dict:
        data = {}

        docs = self._get_docs(pages)
        for lang, sections in docs.items():
            logger.info(f"Indexing {lang} pages...")
            index = self._index_lang(lang, sections)
            data[lang] = {"docs": docs[lang], "index": index}

        return data

    def _get_docs(self, pages: "list[Page]") -> dict[str, TSections]:
        logger.info("Rendering pages for indexing...")
        docs = {}
        for page in pages:
            if page.meta.get("searchable") is False:
                continue
            docs.setdefault(page.lang, {})
            docs[page.lang].update(self._extract_page_data(page))
        return docs

    def _extract_page_data(self, page: "Page") -> TSections:
        html = self.render(page.url)
        data = extract_sections(html, loc=page.url, title=page.title)
        tags = " ".join([f"#{tag}" for tag in page.meta.get("tags", [])])

        if tags:
            data[page.url] = {"title": page.title, "body": tags}

        return data

    def _index_lang(self, lang: str, sections: TSections) -> dict:
        builder = Builder(lang)
        documents = [
            {
                "loc": loc,
                "title": data["title"],
                "body": self._normalize_body(data["body"]),
            }
            for loc, data in sections.items()
        ]
        idx = lunr(
            ref="loc",
            fields=("title", "body"),
            documents=documents,
            builder=builder,
        )
        return idx.serialize()

    def _normalize_body(self, html: str) -> str:
        html  = rx_html_tags.sub("", html)
        html = rx_multiple_spaces.sub(" ", html)
        return html

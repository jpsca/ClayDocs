import typing as t

from lunr import lunr

from ..utils import logger
from .builder import Builder
from .text_extractor import extract_sections


if t.TYPE_CHECKING:
    from ..nav import Page



class Indexer:
    def __init__(self, render: t.Callable) -> None:
        self.render = render

    def index(self, pages: "list[Page]") -> tuple[dict, dict]:
        documents = self._get_documents(pages)
        indexes = {}
        for lang, docs in documents.items():
            logger.info(f"Indexing {lang} pages...")
            indexes[lang] = self._index_lang(lang, docs)

        return documents, indexes

    def _index_lang(self, lang: str, docs: list[dict]) -> dict:
        breakpoint()
        builder = Builder(lang)
        idx = lunr(
            ref="loc",
            fields=("title", "body"),
            documents=docs,
            builder=builder,
        )
        return idx.serialize()

    def _get_documents(self, pages: "list[Page]") -> dict[str, list[dict]]:
        logger.info("Rendering pages for indexing...")
        documents = {}
        for page in pages:
            documents.setdefault(page.lang, [])
            documents[page.lang].extend(self._extract_page_data(page))
        return documents

    def _extract_page_data(self, page: "Page") -> list[dict]:
        data = [
            {
                "loc": page.url,
                "title": page.title,
                "body": ",".join(page.meta.get("tags", [])),
            },
        ]
        html = self.render(page.url)
        data.extend(extract_sections(html, loc=page.url, title=page.title))
        return data

import re
import typing as t

from ..utils import is_debug, logger
from .builder import Builder
from .text_extractor import TSections, extract_sections


if t.TYPE_CHECKING:
    from ..nav import Page


DEBUG = True
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
            data[lang] = {
                "docs": self._filter_docs(docs[lang]),
                "index": index
            }

        return data

    def _filter_docs(self, ldocs: TSections) -> TSections:
        if is_debug():
            return ldocs
        for doc in ldocs.values():
            del doc["raw"]
        return ldocs

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
            data["0"] = {
                "title": page.title,
                "body": "",
                "raw": tags,
                "parent": "",
                "loc": page.url,
            }

        return data

    def _index_lang(self, lang: str, sections: TSections) -> dict:
        if not sections:
            return {}

        builder = Builder(lang)
        builder.ref("uid")
        builder.field("title")
        builder.field("body")

        for uid, data in sections.items():
            builder.add({
                "uid": uid,
                "title": data["title"],
                "body": data["raw"],
            })

        idx = builder.build()
        return idx.serialize()

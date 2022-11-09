import json
import typing as t
from html.parser import HTMLParser

import Stemmer
from lunr import lunr
from lunr.builder import Builder
from lunr.stop_word_filter import generate_stop_word_filter
from lunr.trimmer import trimmer

from .stop_words import stop_words
from .utils import logger


if t.TYPE_CHECKING:
    from .nav import Page
    from .utils import THasRender


STEMMER_LANGS = {
    "eu": "basque",
    "ca": "catalan",
    "da": "danish",
    "nl": "dutch",
    "en": "english",
    "fr": "french",
    "de": "german",
    "el": "greek",
    "it": "italian",
    "no": "norwegian",
    "pt": "portuguese",
    "es": "spanish",
    "sw": "swedish",
}
FIELDS = ("id", "title", "tags", "body")


class DocumentExtractor(HTMLParser):
    START_PAGE = "startpage"
    START_PAGE_COM = f"<!--{START_PAGE}-->"
    ENDPAGE = "endpage"
    start_pos: tuple[int, int]
    end_pos: tuple[int, int]

    def handle_comment(self, data: str) -> None:
        if data == self.START_PAGE:
            self.start_pos = self.getpos()
        elif data == self.ENDPAGE:
            self.end_pos = self.getpos()

    def feed(self, data:str) -> str:
        super().feed(data)
        start_line = self.start_pos[0]
        end_line = self.end_pos[0]
        start_char = self.start_pos[1] + len(self.START_PAGE_COM)
        end_char = self.end_pos[1]
        lines = data.split("\n")
        html = [
            lines[start_line - 1][start_char:],
            *lines[start_line:end_line - 1],
            lines[end_line - 1][:end_char],
        ]
        doc = "\n".join(html)
        return doc


doc_extractor = DocumentExtractor()


class DocsIndex(THasRender if t.TYPE_CHECKING else object):
    def index(self) -> None:
        documents = self._get_documents()
        for lang, documents in documents.items():
            logger.info(f"Indexing {lang} pages...")
            idx = self._index_lang(lang, documents)
            self._store_search_index(lang, idx)

    def _index_lang(self, lang: str, documents: list[dict]) -> dict:
        builder = self._get_builder(lang)
        idx = lunr(
            ref="id",
            fields=FIELDS,
            documents=documents,
            builder=builder,
        )
        return idx.serialize()

    def _store_search_index(self, lang: str, idx: dict) -> None:
        filename = f"search-{lang}.json"
        filepath = self.static_folder / filename
        filepath.write_text(json.dumps(idx))

    def _get_documents(self) -> dict[str, list[dict]]:
        logger.info("Rendering pages for indexing...")
        documents = {}
        for page in self.nav.pages.values():
            documents.setdefault(page.lang, [])
            documents[page.lang].append(
                self._extract_page_data(page)
            )
        return documents

    def _extract_page_data(self, page: "Page") -> dict:
        data = {
            "id": page.url,
            "title": page.title,
            "tags": page.meta.get("tags", []),
            "body": self._extract_page_body(page.url),
        }
        logger.debug(data)
        return data

    def _extract_page_body(self, url: str) -> str:
        breakpoint()
        html = self.render(url)
        return doc_extractor.feed(html)

    def _get_builder(self, lang: str) -> Builder:
        builder = Builder()
        stop_word_filter = self._get_stop_word_filter(lang)
        stemmer = self._get_stemmer(lang)
        builder.pipeline.add(trimmer, stop_word_filter, stemmer)
        builder.search_pipeline.add(stemmer)
        return builder

    def _get_stop_word_filter(self, lang: str) -> t.Callable:
        return generate_stop_word_filter(stop_words[lang], lang)

    def _get_stemmer(self, lang: str) -> Stemmer:
        return Stemmer.Stemmer(STEMMER_LANGS[lang])



import json
import typing as t

import Stemmer
from lunr import lunr
from lunr.builder import Builder
from lunr.stop_word_filter import generate_stop_word_filter

from .text_extractor import extract_text
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

class DocsIndex(THasRender if t.TYPE_CHECKING else object):
    def index(self) -> None:
        documents = self._get_documents()
        print(documents.keys())
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
        logger.info(f"Saving {filepath}...")
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

        log_dict = {k: v for k, v in data.items() if k != "body"}
        log_dict["body"] = "..."
        logger.debug(str(log_dict))
        return data

    def _extract_page_body(self, url: str) -> str:
        html = self.render(url)
        return extract_text(html)

    def _get_builder(self, lang: str) -> Builder:
        builder = Builder()
        stop_word_filter = self._get_stop_word_filter(lang)
        stemmer = self._get_stemmer(lang)

        builder.search_pipeline.register_function(
            stop_word_filter, label=f"stopWordFilter-{lang}"
        )
        builder.search_pipeline.register_function(
            stop_word_filter, label="stopWordFilter"
        )
        builder.search_pipeline.register_function(
            stemmer, label="stemmer"
        )
        return builder

    def _get_stop_word_filter(self, lang: str) -> t.Callable:
        return generate_stop_word_filter(stop_words[lang], lang)

    def _get_stemmer(self, lang: str) -> Stemmer:
        stemmer = Stemmer.Stemmer(STEMMER_LANGS[lang])
        # lunr requires a non-slot-ed object
        def stemmer_func(*args, **kw):
            return stemmer(*args, **kw)

        return stemmer_func




import typing as t

import Stemmer
from lunr.builder import Builder as LunrBuilder
from lunr.pipeline import Pipeline
from lunr.stop_word_filter import generate_stop_word_filter
from lunr.trimmer import trimmer

from .stop_words import stop_words


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


class Builder(LunrBuilder):
    def __init__(self, lang: str) -> None:
        super().__init__()

        stop_word_filter = self._get_stop_word_filter(lang)
        stemmer = self._get_stemmer(lang)

        Pipeline.register_function(stop_word_filter, f"word_filter-{lang}")
        Pipeline.register_function(stemmer, f"stemmer-{lang}")
        self.pipeline.add(trimmer, stop_word_filter, stemmer)

    def add(self, doc, attributes=None):
        """Adds a document to the index.

        Before adding documents to the index it should have been fully
        setup, with the document ref and all fields to index already having
        been specified.

        The document must have a field name as specified by the ref (by default
        this is 'id') and it should have all fields defined for indexing,
        though None values will not cause errors.

        Args:
            - doc (dict): The document to be added to the index.
            - attributes (dict, optional): A set of attributes corresponding
            to the document, currently a single `boost` -> int will be
            taken into account.
        """
        return super().add(doc, attributes=attributes)

    # Private

    def _get_stop_word_filter(self, lang: str) -> t.Callable:
        return generate_stop_word_filter(stop_words[lang], lang)

    def _get_stemmer(self, lang: str) -> Stemmer:
        stemmer = Stemmer.Stemmer(STEMMER_LANGS[lang])

        # lunr requires a non-slot-ed object
        def stemmer_func(*args, **kw):
            return stemmer(*args, **kw)

        return stemmer_func

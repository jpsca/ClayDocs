import typing as t

import Stemmer
from lunr.builder import Builder as LunrBuilder
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

        words_filter = self._get_words_filter(lang)
        stemmer = self._get_stemmer(lang)
        self.pipeline.add(trimmer, words_filter, stemmer)

    # Private

    def _get_words_filter(self, lang: str) -> t.Callable:
        words_filter = generate_stop_word_filter(stop_words[lang], lang)
        self.pipeline.register_function(words_filter, f"words_filter-{lang}")
        return words_filter

    def _get_stemmer(self, lang: str) -> Stemmer:
        stem_word = Stemmer.Stemmer(STEMMER_LANGS[lang]).stemWord

        def stemmer(token, *args, **kw):
            """
            Wrapper for inclusion in pipeline.
            """
            return stem_word(token.string)

        self.pipeline.register_function(stemmer, f"stemmer-{lang}")
        return stemmer

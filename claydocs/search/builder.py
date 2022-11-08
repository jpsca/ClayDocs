import typing as t

import Stemmer
from lunr.builder import Builder
from lunr.stop_word_filter import generate_stop_word_filter
from lunr.trimmer import trimmer

from . import stop_words


stemmer_langs = {
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


def get_stemmer(lang: str) -> Stemmer:
    return Stemmer.Stemmer(stemmer_langs[lang])


def get_stop_word_filter(lang: str) -> t.Callable:
    lang_stop_words = getattr(stop_words, lang)
    return generate_stop_word_filter(lang_stop_words, lang)


def get_builder(lang: str) -> Builder:
    builder = Builder()
    stop_word_filter = get_stop_word_filter(lang)
    stemmer = get_stemmer(lang)
    builder.pipeline.add(trimmer, stop_word_filter, stemmer)
    builder.search_pipeline.add(stemmer)
    return builder

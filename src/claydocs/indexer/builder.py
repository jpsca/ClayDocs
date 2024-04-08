import importlib

from lunr.builder import Builder as LunrBuilder


STEMMER_LANGS = {
    "en": "english",
    "es": "spanish",
}


class Builder(LunrBuilder):
    def __init__(self, lang: str) -> None:
        super().__init__()
        if lang not in STEMMER_LANGS:
            raise ValueError(f"Language {lang} not supported")

        lang_mod = importlib.import_module(f".lunr_{lang}", __package__)

        self.pipeline.reset()
        self.pipeline.register_function(
            lang_mod.trimmer, f"trimmer-{lang}"
        )
        self.pipeline.register_function(
            lang_mod.stop_words_filter, f"words-filter-{lang}"
        )
        self.pipeline.register_function(
            lang_mod.stemmer, f"stemmer-{lang}"
        )
        self.pipeline.add(
            lang_mod.trimmer,
            lang_mod.stop_words_filter,
            lang_mod.stemmer,
        )


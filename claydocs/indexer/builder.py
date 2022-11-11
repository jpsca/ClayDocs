import re
import typing as t
from collections import defaultdict

import Stemmer
from lunr.builder import Builder as LunrBuilder
from lunr.field_ref import FieldRef
from lunr.stop_word_filter import generate_stop_word_filter
from lunr.token import Token
from lunr.tokenizer import Tokenizer as lunr_tokenizer
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


separator = re.compile(r'[\s\-,:!=\[\]()"/]+|(?!\b)(?=[A-Z][a-z])|\.(?!\d)|&[lg]t;')


def tokenizer(obj, metadata=None) -> list[Token]:
    return lunr_tokenizer(obj, metadata=metadata, separator=separator)


class Builder(LunrBuilder):
    def __init__(self, lang: str) -> None:
        super().__init__()

        words_filter = self._get_words_filter(lang)
        stemmer = self._get_stemmer(lang)
        self.pipeline.add(trimmer, words_filter, stemmer)

    def add(self, doc: dict, boost: int = 0) -> None:
        """Adds a document to the index.

        Before adding documents to the index it should have been fully
        setup, with the document ref and all fields to index already having
        been specified.

        The document must have a field name as specified by the ref (by default
        this is 'id') and it should have all fields defined for indexing,
        though None values will not cause errors.

        Args:
        - doc (dict): The document to be added to the index.
        - attributes (dict, optional):
            A set of attributes corresponding
            to the document, currently a single `boost` -> int will be
            taken into account.
        """
        doc_ref = str(doc[self._ref])
        self._documents[doc_ref] = {"boost": boost} if boost else {}
        self.document_count += 1

        for field_name, field in self._fields.items():
            extractor = field.extractor
            field_value = doc[field_name] if extractor is None else extractor(doc)
            tokens = tokenizer(field_value)
            terms = self.pipeline.run(tokens, field_name)
            field_ref = FieldRef(doc_ref, field_name)
            field_terms = defaultdict(int)

            self.field_term_frequencies[str(field_ref)] = field_terms
            self.field_lengths[str(field_ref)] = len(terms)

            for term in terms:
                term_key = str(term)

                field_terms[term_key] += 1
                if term_key not in self.inverted_index:
                    posting = {_field_name: {} for _field_name in self._fields}
                    posting["_index"] = self.term_index  # type: ignore
                    self.term_index += 1
                    self.inverted_index[term_key] = posting

                doc_refs = self.inverted_index[term_key][field_name]
                if doc_ref not in doc_refs:
                    doc_refs[doc_ref] = defaultdict(list)

                for metadata_key in self.metadata_whitelist:
                    metadata = term.metadata[metadata_key]
                    doc_refs[doc_ref][metadata_key].append(metadata)

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

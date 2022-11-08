from lunr import lunr
from lunr.index import Index

from .builder import get_builder


def build_index(*, lang, ref: str = "id", **kw) -> Index:
    builder = get_builder(lang)
    return lunr(builder=builder, **kw)

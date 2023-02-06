from ..utils import Page, is_debug, logger
from .builder import Builder
from .text_extractor import TSections, extract_sections


def index_pages(pages: list[Page]) -> dict:
    data = {}
    docs = _get_docs(pages)

    for lang, sections in docs.items():
        logger.info(f"Indexing {lang} pages...")
        index = _index_lang(lang, sections)
        data[lang] = {
            "docs": _filter_docs(docs[lang]),
            "index": index
        }

    return data


def _filter_docs(ldocs: TSections) -> TSections:
    if is_debug():
        return ldocs
    for doc in ldocs.values():
        del doc["raw"]
    return ldocs


def _get_docs(pages: list[Page]) -> dict[str, TSections]:
    logger.info("Rendering pages for indexing...")
    docs = {}
    for page in pages:
        if page.meta.get("searchable") is False:
            continue
        docs.setdefault(page.lang, {})
        docs[page.lang].update(_extract_page_data(page))
    return docs


def _extract_page_data(page: Page) -> TSections:
    data = extract_sections(page.html, loc=page.url, title=page.title)
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


def _index_lang(lang: str, sections: TSections) -> dict:
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

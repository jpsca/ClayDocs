import json
import os
import re
import tempfile
import typing as t
from pathlib import Path

from ..utils import Page, is_debug, logger
from .text_extractor import TDoc, extract_docs, make_doc


INDEXABLE_JSON = "docs-{lang}.json"
INDEX_JSON = "search-{lang}.json"
INDEXER = "indexer.js"
rx_html_tags = re.compile(r"</?[a-z]+[1-6]?( open)?>")


class Indexer:
    def __init__(self, root: Path, render: t.Callable) -> None:
        self.root = root
        self.render = render

    def index(self, pages: list[Page]) -> dict:
        data = {}
        docs = self._get_docs(pages)

        for lang, sections in docs.items():
            logger.info(f"Indexing {lang} pages...")
            index = self._index_lang(lang, sections)
            data[lang] = {
                "docs": self._remove_raw_data(docs[lang]),
                "index": index
            }

        return data

    # Private

    def _remove_raw_data(self, docs: list[TDoc]) -> list[TDoc]:
        if is_debug():
            return docs
        for doc in docs:
            if not doc["id"].startswith("tags-"):
                del doc["raw"]
        return docs

    def _get_docs(self, pages: list[Page]) -> dict[str, list[TDoc]]:
        logger.info("Rendering pages for indexing...")
        docs = {}
        for page in pages:
            if page.meta.get("searchable") is False:
                continue
            docs.setdefault(page.lang, [])
            docs[page.lang].extend(self._extract_page_data(page))
        return docs

    def _extract_page_data(self, page: Page) -> list[TDoc]:
        html = self.render(page.url)
        data = extract_docs(html, loc=page.url, title=page.title)
        tags = " ".join([f"#{tag}" for tag in page.meta.get("tags", [])])

        if tags:
            data.append(make_doc(
                id=f"tags-{page.url}",
                title=page.title,
                raw=tags,
                loc=page.url,
            ))

        return data

    def _index_lang(self, lang: str, sections: list[TDoc]) -> dict:
        if not sections:
            return {}

        out_path = Path(tempfile.mkdtemp())
        docs_path = out_path / INDEXABLE_JSON.format(lang=lang)
        index_path = out_path / INDEX_JSON.format(lang=lang)
        docs_path.write_text(json.dumps(sections, ensure_ascii=False))

        indexer_path = self.root / INDEXER
        if (not indexer_path.is_file()):
            raise ValueError(f"{indexer_path} not found! Unable to activate search")

        cmd = f"node {indexer_path} {lang} {out_path}"
        print(">>>  ", cmd)
        os.system(cmd)
        index = json.loads(index_path.read_text())

        docs_path.unlink()
        index_path.unlink()
        out_path.rmdir()
        return index

import re
import shutil
import typing as t
from pathlib import Path

from html2image import Html2Image

from .utils import Page, THasRender, logger, print_random_messages


RX_ABS_URL = re.compile(
    r"""\s(src|href|data-[a-z0-9_-]+)\s*=\s*['"](\/(?:[a-z0-9_-][^'"]*)?)[\'"]""",
    re.IGNORECASE,
)
SOCIAL_CARD_SIZE = (1200, 630)


class DocsBuilder(THasRender if t.TYPE_CHECKING else object):
    relativize_static: bool = False
    hti: Html2Image

    def build(self) -> None:
        self.build_folder.mkdir(exist_ok=True)
        self.build_folder_static.mkdir(exist_ok=True)

        logger.info("Copying static folder...")
        self._copy_static_folder()

        logger.info("Rendering pages...")
        self.hti = Html2Image()

        for url in self.nav.pages:
            page = self.nav.get_page(url)
            if not page:
                logger.error(f"Page not found: {url}")
                continue
            self._build_page(page)
            self._build_social_card(page)

        logger.info("   ...")
        print_random_messages()
        logger.info("✨ Done! ✨")

    def _build_page(self, page: Page) -> None:
        url = page.url.strip("/")
        filename = f"{url}/index.html".lstrip("/")
        filepath = self.build_folder / filename
        folderpath = filepath.parent
        folderpath.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Rendering page {url}")
        html = self.render_page(page)

        logger.debug("Relativizing page URLs")
        html = self._fix_urls(html, filename)

        logger.info("Writing file")
        filepath.write_text(html)


    def _build_social_card(self, page: Page) -> None:
        url = page.url.strip("/")
        filename = f"{url}/og-card.html".lstrip("/")
        filepath = self.build_folder / filename
        folderpath = filepath.parent

        logger.debug(f"Rendering social card for page {url}")
        html = self.render_social_card(page)
        html = self._fix_urls(html, filename, relativize_static=True)
        filepath.write_text(html)

        logger.info("Generating social card")
        self.hti.output_path = folderpath
        self.hti.screenshot(
            url=str(filepath),
            size=SOCIAL_CARD_SIZE,
            save_as="og-card.png",
        )
        filepath.unlink()

    def _copy_static_folder(self) -> None:
        shutil.copytree(
            self.static_folder,
            self.build_folder_static,
            dirs_exist_ok=True,
        )

    def _fix_urls(
        self,
        html: str,
        filename: str,
        relativize_static: bool | None = None,
    ) -> str:
        pos = 0
        relativize_static = (
            self.relativize_static
            if relativize_static is None
            else relativize_static
        )

        while True:
            match = RX_ABS_URL.search(html, pos=pos)
            if not match:
                break

            attr, url = match.groups()
            if url.startswith(self.static_url):
                newurl = self._fix_static_url(url)
                if relativize_static:
                    newurl = self._get_relative_url(newurl, filename)
            else:
                newurl = self._get_relative_url(url, filename)
                if not newurl.endswith("/"):
                    newurl = f"{newurl}/"

            logger.debug(f"{url} -> {newurl}")
            pos = match.end()
            html = f'{html[:match.start()]} {attr}="{newurl}"{html[pos:]}'

        return html

    def _fix_static_url(self, current_url: str) -> str:
        url = current_url.rsplit("?", 1)[0]

        filepath = self.build_folder_static / url.removeprefix(self.static_url).lstrip(
            "/"
        )
        if not filepath.exists():
            logger.debug(f"{filepath} doesn't exists")
            self._download_url(url, filepath)

        return url

    def _download_url(self, url: str, filepath: Path) -> None:
        logger.debug(f"Downloading {url}...")
        sf = self.server.application.find_file(url)
        if sf is None:
            logger.error(f"{url} doesn't exists")
            return
        src_path, _ = sf.get_path_and_headers({})
        filepath.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src_path, filepath)
        logger.debug(f"Created {filepath}")

    def _get_relative_url(self, current_url: str, filename: str) -> str:
        filename = filename.removesuffix("index.html")
        depth = filename.count("/")
        url = ("../" * depth) + current_url.lstrip("/")

        if not url.startswith("."):
            url = f"./{url}"
        return url

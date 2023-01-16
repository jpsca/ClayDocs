import re
import shutil
import typing as t

from .utils import logger, print_random_messages

if t.TYPE_CHECKING:
    from pathlib import Path
    from .utils import THasRender


RX_ABS_URL = re.compile(
    r"""\s(src|href|data-[a-z0-9_-]+)\s*=\s*['"](\/(?:[a-z0-9_-][^'"]*)?)[\'"]""",
    re.IGNORECASE,
)


class DocsBuilder(THasRender if t.TYPE_CHECKING else object):
    relativize_static: bool = False

    def build(self) -> None:
        logger.info("Rendering pages...")
        self.build_folder.mkdir(exist_ok=True)
        self.build_folder_static.mkdir(exist_ok=True)

        logger.info("Copying static folder")
        self._copy_static_folder()

        for url in self.nav.pages:
            page = self.nav.get_page(url)
            if not page:
                logger.error(f"Page not found: {url}")
                continue

            filename = page.url.strip("/")
            filename = f"{filename}/index.html".lstrip("/")
            filepath = self.build_folder / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)

            html = self.render_page(page)
            logger.debug("Relativizing URLs")
            html = self._fix_urls(html, filename)

            logger.info(f"Writing {filename}")
            filepath.write_text(html)

        logger.info("...")
        print_random_messages()
        logger.info("✨ Done! ✨")

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
    ) -> str:
        pos = 0

        while True:
            match = RX_ABS_URL.search(html, pos=pos)
            if not match:
                break

            attr, url = match.groups()
            if url.startswith(self.static_url):
                newurl = self._fix_static_url(url)
                if self.relativize_static:
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

    def _download_url(self, url: str, filepath: "Path") -> None:
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

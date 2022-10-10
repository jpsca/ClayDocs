import re
import typing as t

from .utils import logger

if t.TYPE_CHECKING:
    from pathlib import Path
    from .nav import Nav


class HasRender:
    BUILD_FOLDER: str
    build_folder: "Path"
    nav: "Nav"

    def print_random_messages(self, num=2) -> None:  # type: ignore
        ...

    def render(self, name: str, **kw) -> str:  # type: ignore
        ...


RX_ABS_URL = re.compile(
    r"""\s(src|href|data-[a-z0-9_-]+)\s*=\s*['"](\/(?:[a-z0-9_-][^'"]*)?)[\'"]""",
    re.IGNORECASE,
)


class DocsBuilder(HasRender if t.TYPE_CHECKING else object):
    def build(self) -> None:
        logger.info("Rendering pages...")

        for url in self.nav.titles:
            name = url.strip("/")
            if name.endswith("/index") or name == "index":
                filename = f"{name}.html"
            else:
                filename = f"{name}/index.html"
            filepath = self.build_folder / filename
            folder = filepath.parent
            logger.info(folder)
            folder.mkdir(parents=True, exist_ok=True)

            html = self.render(name)

            logger.debug("Relativizing URLs")
            pass

            logger.info(f"{self.BUILD_FOLDER}/{filename}")
            filepath.write_text(html)

        self.print_random_messages()
        print("\n✨ Done! ✨")

    def relativize_urls(
        self,
        html: str,
        base_path: "Path",
        relpath: str,
    ) -> str:
        relpath = str(relpath)

        for attr, url in RX_ABS_URL.findall(html):
            newurl = self._get_relative_url(url, base_path, relpath)
            repl = r' %s="%s"' % (attr, newurl)
            html = re.sub(RX_ABS_URL, repl, html, count=1)

        return html

    def _get_relative_url(
        self,
        curent_url: str,
        base_path: "Path",
        relpath: str,
    ) -> str:
        depth = relpath.count("/")
        url = (r"../" * depth) + curent_url.lstrip("/")

        if not url:
            return "index.html"
        if (base_path / relpath).is_dir() or url.endswith("/"):
            return url.rstrip("/") + "/index.html"

        return url

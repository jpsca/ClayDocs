import typing as t

import jinja2

from .exceptions import Abort
from .utils import logger, print_random_messages
from .server import LiveReloadServer

if t.TYPE_CHECKING:
    from .utils import THasRender


class DocsServer(THasRender if t.TYPE_CHECKING else object):
    server: "LiveReloadServer"

    def __init_server__(self) -> None:
        server = LiveReloadServer(
            get_page=self.get_cached_page,
            refresh=self.refresh,
        )

        middleware = self.catalog.get_middleware(
            server.application,
            allowed_ext=None,  # All file extensions allowed as static files
            autorefresh=True,
        )
        middleware.add_files(self.static_folder, self.STATIC_URL)
        middleware.add_files(self.temp_folder, self.THUMBNAILS_URL)
        server.application = middleware  # type: ignore
        self.server = server

    def serve(self) -> None:
        print_random_messages()
        logger.info("Starting server...")
        try:
            server = self.server
            server.watch(self.content_folder)
            server.watch(self.static_folder)
            for path in self.catalog.paths:
                server.watch(path)

            try:
                server.serve()
            except KeyboardInterrupt:
                print()  # To clear the printed ^C
            finally:
                server.shutdown()
        except jinja2.exceptions.TemplateError:
            # This is a subclass of OSError, but shouldn't be suppressed.
            raise
        except OSError as err:  # pragma: no cover
            # Avoid ugly, unhelpful traceback
            print(f"{type(err).__name__}: {err}")
            raise Abort(f"{type(err).__name__}: {err}")

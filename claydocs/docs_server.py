import jinja2
import typing as t

from .exceptions import Abort
from .utils import logger, print_random_messages
from .wsgi import LiveReloadServer

if t.TYPE_CHECKING:
    from .utils import THasRender


class DocsServer(THasRender if t.TYPE_CHECKING else object):
    def serve(self) -> None:
        logger.info("Starting server...")
        print_random_messages()
        try:
            server = self.get_server()
            server.watch(self.content_folder)
            server.watch(self.components_folder)
            server.watch(self.theme_folder)
            server.watch(self.static_folder)

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
            raise Abort(f"{type(err).__name__}: {err}")

    def get_server(self) -> "LiveReloadServer":
        server = LiveReloadServer(render=self.render)

        middleware = self.catalog.get_middleware(
            server.application,
            allowed_ext=None,  # All file extensions allowed as static files
            autorefresh=True,
        )
        middleware.add_files(self.static_folder, self.STATIC_URL)
        server.application = middleware  # type: ignore
        return server

import html
import logging
import re
import socketserver
import traceback
import threading
import typing as t
import wsgiref.simple_server
from pathlib import Path
from urllib.parse import quote
from sys import exc_info

import watchdog.events
import watchdog.observers.polling
from watchdog.observers import Observer

from .utils import logger, timestamp


DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8080
START_MESSAGE = """
─────────────────────────────────────────────────
 Running on {addr}
 Press [Ctrl]+[C] to quit
─────────────────────────────────────────────────
"""
STATIC_FILES = ("/favicon.ico", "/robots.txt", "/humans.txt")
LIVERELOAD_URL = "/livereload/"
RX_LIVERELOAD = re.compile(rf"{LIVERELOAD_URL}([0-9]+)/?")

HTTP_OK = "200 OK"
HTTP_NOT_FOUND = "404 Not Found"
HTTP_ERROR = "500 Internal Server Error"
ERROR_BODY = """<body>
<title>{title}</title>
<h1>{title}</h1>
<h2><pre>{error}</pre></h2>
<pre>{traceback}</pre>
</body>
"""

HERE = Path(__file__).parent
SCRIPT_TEMPLATE = (HERE / "livereload.js").read_text()

rx_index = re.compile(r"/index$", re.IGNORECASE)


class LiveReloadServer(socketserver.ThreadingMixIn, wsgiref.simple_server.WSGIServer,):
    daemon_threads = True
    poll_response_timeout = 60

    def __init__(
        self,
        get_page: t.Callable,
        refresh: t.Callable,
        *,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        shutdown_delay: float = 1,
        **kwargs,
    ) -> None:
        self._get_page = get_page
        self._refresh = refresh

        self.host = host
        self.port = port
        self.shutdown_delay = shutdown_delay

        # This version of the docs
        self.epoch = timestamp()
        # Must be held when accessing epoch
        self.epoch_cond = threading.Condition()

        self.must_refresh = False
        # Must be held when accessing must_refresh.
        self.must_refresh_cond = threading.Condition()

        self.serve_thread = threading.Thread(
            target=lambda: self.serve_forever(shutdown_delay)
        )
        self.observer = watchdog.observers.polling.PollingObserver()
        self.watch_refs: dict[str, Observer] = {}
        self.running = False

        super().__init__((host, port), RequestHandler, **kwargs)

    def watch(self, path_to_watch: Path, recursive: bool = True) -> None:
        """Add the 'path' to watched paths, call the function and reload
        when any file changes under it."""
        path = str(path_to_watch.absolute())
        if path in self.watch_refs:
            return

        def callback(event):
            if event.is_directory:
                return
            logger.debug(str(event))
            with self.must_refresh_cond:
                self.must_refresh = True
                self.must_refresh_cond.notify_all()
            self._refresh(event.src_path)

        handler = watchdog.events.FileSystemEventHandler()
        handler.on_any_event = callback
        logger.debug(f"Watching '{path}'")
        self.watch_refs[path] = self.observer.schedule(
            handler, path, recursive=recursive
        )

    def application(self, environ: dict, start_response: t.Callable) -> list[bytes]:
        self.request = Request(environ)
        path = self.request.path
        if path.startswith(LIVERELOAD_URL):
            return self.livereload(path, start_response)

        self.headers = {"Server": "claydocs"}
        str_body, status = self.call()
        body = str_body.encode("utf8")
        body = self._inject_js_into_html(body)

        self.headers["Content-Length"] = str(len(body))
        start_response(status, list(self.headers.items()))
        return [body]

    def livereload(self, path: str, start_response: t.Callable) -> list[bytes]:
        headers = [("Content-Type", "text/plain")]
        match = RX_LIVERELOAD.fullmatch(path)
        if not match:
            start_response(HTTP_NOT_FOUND, headers)
            return [b""]

        start_response(HTTP_OK, headers)
        epoch = int(match[1])

        def condition():
            return self.epoch > epoch

        with self.epoch_cond:
            if not condition():
                # Stall the browser, respond as soon as there's something new.
                # If there's not, respond anyway after a timeout
                self.epoch_cond.wait_for(condition, timeout=self.poll_response_timeout)
            return [b"%d" % self.epoch]

    def call(self) -> tuple[str, str]:
        if self.request.path in STATIC_FILES:
            return self.redirect_to(f"/static{self.request.path}")

        if self.request.path.endswith("/index"):
            url = rx_index.sub("/", self.request.path)
            return self.redirect_to(url)

        status = HTTP_OK
        if self.request.method == "HEAD":
            body = ""
        else:
            body, status = self.get_page()

        self.headers.setdefault("Content-Type", "text/html; charset=utf-8")
        return body, status

    def redirect_to(self, path: str) -> tuple[str, str]:
        location = quote(path.encode("utf8"))
        self.headers["Location"] = location
        logger.info(f"{self.request.path} -> {location}")
        return "", "302 Found"

    def get_page(self) -> tuple[str, str]:
        path = self.request.path
        try:
            body = self._get_page(path.rstrip("/"))
        except Exception as exception:
            logger.exception(path)
            return self.render_error_page(exception)

        if body:
            return body, HTTP_OK

        if path.endswith("/"):
            path = f"{path}index"
        return f"{path} not found", HTTP_NOT_FOUND

    def render_error_page(self, exception: Exception) -> tuple[str, str]:
        body = ERROR_BODY.format(
            title=html.escape(exception.__class__.__name__),
            error=html.escape(str(exception)),
            traceback=html.escape("".join(traceback.format_exception(*exc_info()))),
        )
        return body, HTTP_ERROR

    def serve(self) -> None:
        self.running = True
        self.observer.start()
        print(START_MESSAGE.format(addr=f"http://{self.host}:{self.port}"))
        self.serve_thread.start()
        self.refresh_loop()

    def refresh_loop(self) -> None:
        while True:
            with self.must_refresh_cond:
                while not self.must_refresh_cond.wait_for(
                    lambda: self.must_refresh or not self.running,
                    timeout=self.shutdown_delay,
                ):
                    # We could have used just one wait instead of a loop + timeout, but we need
                    # occasional breaks, otherwise on Windows we can't receive KeyboardInterrupt.
                    pass
                if not self.running:
                    return
                logger.info("Detected file changes")
                self.must_refresh = False

            with self.epoch_cond:
                logger.info("Reloading page...")
                self.epoch = timestamp()
                self.epoch_cond.notify_all()

    def shutdown(self) -> None:
        self.observer.stop()
        logger.info("Shutting down...")
        self.running = False

        if self.serve_thread.is_alive():
            super().shutdown()

    def _inject_js_into_html(self, content: bytes) -> bytes:
        try:
            body_end = content.rindex(b"</body>")
        except ValueError:
            body_end = len(content)
        # The page will reload if the livereload poller returns a newer epoch than what it knows.
        with self.epoch_cond:
            script = SCRIPT_TEMPLATE.replace("__EPOCH__", str(self.epoch))

        return b"%b<script>%b</script>%b" % (
            content[:body_end],
            script.encode(),
            content[body_end:],
        )


class RequestHandler(wsgiref.simple_server.WSGIRequestHandler):
    def log_request(
        self,
        code: str = "200",
        _size: int | str = "-",
    ) -> None:
        message = self.path
        code = str(code)
        if code.startswith("5"):
            level = logging.ERROR
        elif code.startswith("4"):
            level = logging.WARNING
            if code == "404":
                message = f"{self.path} - NOT FOUND"
        elif self.path.startswith(LIVERELOAD_URL):
            level = logging.DEBUG
        else:
            level = logging.INFO

        logger.log(level, message)

    def log_message(self, format: str, *args) -> None:
        logger.debug(format, *args)


class Request:
    def __init__(self, environ: t.Optional[dict] = None, path: str = "") -> None:
        environ = environ or {}
        self.environ = environ
        self.path = path or self.get_path()
        self.method = environ.get("REQUEST_METHOD", "GET").upper()
        self.remote_addr = environ.get("REMOTE_ADDR", "127.0.0.1")

    def get_path(self) -> str:
        path_info = self.environ.get("PATH_INFO")
        if not path_info:
            return "/"
        path = path_info.encode("iso-8859-1", "replace").decode("utf-8", "replace")
        return path

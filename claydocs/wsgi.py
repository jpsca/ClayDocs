import logging
import re
import socketserver
import string
import time
import traceback
import threading
import typing as t
import wsgiref.simple_server
from urllib.parse import quote
from sys import exc_info

import watchdog.events
import watchdog.observers.polling

from .utils import logger

if t.TYPE_CHECKING:
    from pathlib import Path
    from watchdog.observers import ObservedWatch


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080
START_MESSAGE = """
─────────────────────────────────────────────────
 Running at {addr}
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
<h2>{error}</h2>
<pre>{traceback}</pre>
</body>
"""
SCRIPT_TEMPLATE_STR = """
var livereload = function(epoch) {
    var req = new XMLHttpRequest();
    req.onloadend = function() {
        if (parseFloat(this.responseText) > epoch) {
            location.reload();
            return;
        }
        var launchNext = livereload.bind(this, epoch);
        if (this.status === 200) {
            launchNext();
        } else {
            setTimeout(launchNext, 3000);
        }
    };
    req.open("GET", "/livereload/" + epoch);
    req.send();

    console.log('Enabled live reload');
}
livereload(${epoch});
"""
SCRIPT_TEMPLATE = string.Template(SCRIPT_TEMPLATE_STR)


def _timestamp() -> int:
    return round(time.monotonic() * 1000)


class LiveReloadServer(socketserver.ThreadingMixIn, wsgiref.simple_server.WSGIServer):
    daemon_threads = True
    poll_response_timeout = 60

    def __init__(
        self,
        render: "t.Callable",
        *,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        polling_interval: float = 0.5,
        shutdown_delay: float = 0.25,
        **kwargs
    ) -> None:
        self._render = render
        self.host = host
        self.port = port
        self.polling_interval = polling_interval
        self.shutdown_delay = shutdown_delay

        self.epoch = _timestamp()  # This version of the docs
        self.epoch_cond = threading.Condition()  # Must be held when accessing epoch.
        self.must_refresh = False
        self.must_refresh_cond = threading.Condition()  # Must be held when accessing must_refresh.

        self.serve_thread = threading.Thread(
            target=lambda: self.serve_forever(shutdown_delay)
        )
        self.observer = watchdog.observers.polling.PollingObserver(
            timeout=polling_interval
        )
        self.watch_refs: "dict[str, ObservedWatch]" = {}
        self.running = False

        super().__init__((host, port), RequestHandler, **kwargs)

    def watch(self, path: "Path", recursive: bool = True) -> None:
        """Add the 'path' to watched paths, call the function and reload when any file changes under it."""
        path = str(path.absolute())
        if path in self.watch_refs:
            return

        def callback(event):
            if event.is_directory:
                return
            logger.debug(str(event))
            with self.must_refresh_cond:
                self.must_refresh = True
                self.must_refresh_cond.notify_all()

        handler = watchdog.events.FileSystemEventHandler()
        handler.on_any_event = callback
        logger.debug(f"Watching '{path}'")
        self.watch_refs[path] = self.observer.schedule(
            handler, path, recursive=recursive
        )

    def application(self, environ, start_response):
        self.request = Request(environ)
        path = self.request.path
        if path.startswith(LIVERELOAD_URL):
            return self.livereload(path, start_response)

        self.headers = {"Server": "ClayDocs"}
        body, status = self.call()
        if hasattr(body, "encode"):
            body = body.encode("utf8")
        body = self._inject_js_into_html(body)

        self.headers["Content-Length"] = str(len(body))
        start_response(status, list(self.headers.items()))
        return [body]

    def livereload(self, path, start_response):
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

    def call(self):
        if self.request.path in STATIC_FILES:
            return self.redirect_to(f"/static{self.request.path}")

        status = HTTP_OK
        if self.request.method == "HEAD":
            body = ""
        else:
            body, status = self.render_page()

        self.headers.setdefault("Content-Type", "text/html")
        return body, status

    def redirect_to(self, path):
        location = quote(path.encode("utf8"))
        self.headers["Location"] = location
        logger.info(f"{self.request.path} -> {location}")
        return "", "302 Found"

    def render_page(self):
        path = self.request.path
        try:
            body = self._render(path[1:])
        except Exception as exception:
            logger.exception(path)
            return self.render_error_page(exception), HTTP_ERROR

        if body:
            return body, HTTP_OK
        else:
            return f"{path}.md not found", HTTP_NOT_FOUND

    def render_error_page(self, exception):
        return ERROR_BODY.format(
            title=exception.__class__.__name__,
            error=str(exception),
            traceback="".join(traceback.format_exception(*exc_info())),
        )

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
                    lambda: self.must_refresh or not self.running, timeout=self.shutdown_delay
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
                self.epoch = _timestamp()
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
            script = SCRIPT_TEMPLATE.substitute(epoch=self.epoch)

        return b"%b<script>%b</script>%b" % (
            content[:body_end],
            script.encode(),
            content[body_end:],
        )


class RequestHandler(wsgiref.simple_server.WSGIRequestHandler):
    def log_request(self, code="200", size="-"):
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

    def log_message(self, format, *args):
        logger.debug(format, *args)


class Request:
    def __init__(self, environ=None, path=None):
        environ = environ or {}
        self.environ = environ
        self.path = path or self.get_path()
        self.method = environ.get("REQUEST_METHOD", "GET").upper()
        self.remote_addr = environ.get("REMOTE_ADDR", "127.0.0.1")

    def get_path(self):
        path_info = self.environ.get("PATH_INFO")
        if not path_info:
            return "/"
        path = path_info.encode("iso-8859-1", "replace").decode("utf-8", "replace")
        if path.endswith("/"):
            return path + "index"
        return path
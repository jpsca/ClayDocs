import traceback
from urllib.parse import quote
from sys import exc_info

from gunicorn.app.base import BaseApplication

from .utils import LOGGER_NAME, logger


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080
START_MESSAGE = """
─────────────────────────────────────────────────
Running at {addr}
Press [Ctrl]+[C] to quit
─────────────────────────────────────────────────
"""
STATIC_FILES = ("favicon.ico", "robots.txt", "humans.txt")

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


class WSGIApp:
    def __init__(self, docs):
        self.docs = docs
        super().__init__()

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        self.headers = {"Server": "ClayDocs"}
        body, status = self.call(request)
        if hasattr(body, "encode"):
            body = body.encode("utf8")

        self.headers["Content-Length"] = str(len(body))
        start_response(status, list(self.headers.items()))
        return [body]

    def call(self, request):
        path = request.path
        if path in STATIC_FILES:
            return self.redirect_to(f"/static/{path}")

        status = HTTP_OK
        if request.method == "HEAD":
            body = ""
        else:
            body, status = self.render_page(path, request)

        self.headers.setdefault("Content-Type", "text/html")
        return body, status

    def redirect_to(self, path):
        self.headers["Location"] = quote(path.encode("utf8"))
        logger.info("Redirecting to: %s", self.headers["Location"])
        return "", "302 Found"

    def render_page(self, path, request):
        try:
            body = self.docs.render(path, request=request)
        except Exception as exception:
            logger.exception(f"/{path}")
            return self.render_error_page(exception), HTTP_ERROR

        if body:
            return body, HTTP_OK
        else:
            logger.error(f"/{path} - Not Found")
            return f"{path}.md not found", HTTP_NOT_FOUND

    def render_error_page(self, exception):
        return ERROR_BODY.format(
            title=exception.__class__.__name__,
            error=str(exception),
            traceback="".join(traceback.format_exception(*exc_info())),
        )

    def run(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
        def on_starting(server):
            print(START_MESSAGE.format(addr=f"http://{host}:{port}"))

        def on_exit(server):
            print()  # To cleanup the printed "^C"
            logger.info("Shutting down...")

        server = GunicornBaseApplication(
            self,
            bind=f"{host}:{port}",
            accesslog=None,
            loglevel="error",
            reload=True,
            reload_extra_files="docs.py",
            on_starting=on_starting,
            on_exit=on_exit,
        )
        server.run()


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
            return ""
        path = path_info.encode("iso-8859-1", "replace").decode("utf-8", "replace")
        if path.endswith("/"):
            return path[1:] + "index"
        return path[1:]


class GunicornBaseApplication(BaseApplication):
    def __init__(self, app, **options):
        self.app = app
        self.options = options
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        return self.app

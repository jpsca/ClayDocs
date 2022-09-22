import mimetypes
import traceback
from urllib.parse import quote

from gunicorn.app.base import BaseApplication


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
START_MESSAGE = """
 ─────────────────────────────────────────────────
  ClayDocs running at {addr}

  Press [Ctrl]+[C] to quit
 ─────────────────────────────────────────────────
"""
STATIC_FILES = ("favicon.ico", "robots.txt", "humans.txt")
HTTP_OK = "200 OK"
HTTP_ERROR = "500 Internal Server Error"
ERROR_BODY = """<body>
<title>{title}</title>
<h1>{title}</h1>
<h2><var>{path}</var></h2>
<h3>{error}</h3>
<pre>{traceback}</pre>
</body>
"""


def on_starting(server):
    """Gunicorn hook"""
    host, port = server.address[0]
    print(START_MESSAGE.format(addr=f"http://{host}:{port}"))


class WSGIApp:
    def __init__(self, docs):
        self.docs = docs
        super().__init__()

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        body, status, headers = self.call(request)
        if hasattr(body, "encode"):
            body = body.encode("utf8")

        headers.append(("Content-Length", str(len(body))))
        start_response(status, headers)
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

        mime = mimetypes.guess_type(path)[0] or "text/plain"
        response_headers = [
            ("Server", "ClayDocs"),
            ("Content-Type", mime),
            ("Content-Type", "text/html")
        ]
        return body, status, response_headers

    def redirect_to(self, path):
        return "", "302 Found", [("Location", quote(path.encode("utf8")))]

    def render_page(self, path, request):
        try:
            return self.docs.render(path, request=request), HTTP_OK
        except Exception as exception:
            return self.render_error_page(exception), HTTP_ERROR

    def render_error_page(self, exception):
        return ERROR_BODY.format(
            title=exception.__class__.__name__,
            path=exception.args[0],
            error=exception.args[1],
            traceback="".join(traceback.format_exception(exception))
        )

    def run(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
        server = GunicornBaseApplication(
            self,
            bind=f"{host}:{port}",
            accesslog=None,
            loglevel="error",
            on_starting=on_starting
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

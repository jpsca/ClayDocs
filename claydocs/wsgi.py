import mimetypes
from urllib.parse import quote

from gunicorn.app.base import BaseApplication


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000


class WSGIApp(BaseApplication):
    def __init__(self, docs, host=DEFAULT_HOST, port=DEFAULT_PORT, **kw):
        self.docs = docs
        kw.setdefault("bind", f"{host}:{port}")
        kw.setdefault("accesslog", "-")
        kw.setdefault("access_log_format", "%(h)s %(m)s %(U)s -> HTTP %(s)s")
        super().__init__(**kw)

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
        print(path)
        if request.method == "HEAD":
            body = ""
        else:
            print("rendering file", path)
            body = self.docs.render(path, request=request)

        mime = mimetypes.guess_type(path)[0] or "text/plain"
        response_headers = [("Content-Type", mime)]
        return body, "200 OK", response_headers

    def redirect_to(self, path):
        return "", "302 Found", [("Location", quote(path.encode("utf8")))]


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
        return path[1:] + "index.html" if path.endswith("/") else path[1:]

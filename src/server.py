"""Модуль простого веб сервера."""
import mimetypes
import os
import urllib.request
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

from src.path import ROOT_DIR

PAGES_DIR = os.path.join(ROOT_DIR, "pages")
STATIC_DIR = os.path.join(ROOT_DIR, "static")

REMOTE_PAGES_URL = "https://github.com/matt-motik/sp-django/tree/feature/base_web/pages/"

PAGE_FILES = ["index.html", "catalog.html", "category.html",
              "contacts.html", "404.html", "500.html"]
EXTRA_MIME = {
    ".css":  "text/css; charset=utf-8",
    ".js":   "text/javascript; charset=utf-8",
    ".woff": "font/woff",
    ".woff2":"font/woff2",
}

def read_page(name: str) -> str:
    """Чтение HTML-файла через контекстный менеджер."""
    if name[0] == "/":
        name = name[1:]
    if name not in PAGE_FILES:
        name = "index.html"
    with open(os.path.join(PAGES_DIR, name), "r", encoding="utf-8") as fh:
        return fh.read()


class Handler(BaseHTTPRequestHandler):

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, code: int, html: str) -> None:
        self._send(code, html.encode("utf-8"), "text/html; charset=utf-8")

    def _send_static(self, file_path: str) -> None:
        ext = os.path.splitext(file_path)[1].lower()
        content_type = (EXTRA_MIME.get(ext)
                        or mimetypes.guess_type(file_path)[0]
                        or "application/octet-stream")
        with open(file_path, "rb") as fh:
            self._send(200, fh.read(), content_type)


    def do_GET(self):
        path = self.path.split("?")[0]
        print(f"[GET] {path}")
        #
        if self.path.startswith("/static/"):
            real = os.path.abspath(os.path.join(STATIC_DIR, path[len("/static/"):]))
            if real.startswith(STATIC_DIR + os.sep) and os.path.isfile(real):
                self._send_static(real)
            else:
                self._send_html(404, read_page("404.html"))
            return
        try:
            # страницы ошибок
            if path.startswith("/404"):
                self._send_html(404, read_page("404.html"))
            elif self.path.startswith("/500"):
                self._send_html(500, read_page("500.html"))
            else:
                # по заданию: ЛЮБОЙ GET-запрос возвращает страницу «Контакты»
                self._send_html(200, read_page(path))
        except FileNotFoundError as exc:
            print("Файл не найден:", exc)
            self._send_html(404, "<h1>404 — страница не найдена</h1>")
        except Exception as exc:
            print("Ошибка сервера:", exc)
            self._send_html(500, "<h1>500 — внутренняя ошибка сервера</h1>")

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8")
        print(f"[POST] {self.path}, сырые данные: {raw}")
        print("Приняты данные от пользователя:")
        for key, values in parse_qs(raw).items():
            print(f"  {key} = {', '.join(values)}")
        try:
            self._send_html(200, read_page("contacts.html"))
        except Exception:
            self._send_html(200, "<h1>Данные получены!</h1>")






"""Модуль простого веб сервера."""
import posixpath
from functools import wraps
from http.server import BaseHTTPRequestHandler
import mimetypes
import os
from urllib.parse import parse_qs, unquote

from src.path import ROOT_DIR

PAGES_DIR = os.path.join(ROOT_DIR, "pages")
STATIC_DIR = os.path.join(ROOT_DIR, "static")

REMOTE_PAGES_URL = "https://github.com/matt-motik/sp-django/tree/feature/base_web/pages/"

PAGE_FILES = ["index.html", "catalog.html", "category.html", "contacts.html", "404.html", "500.html"]
EXTRA_MIME = {
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
}


def path_guard(func):
    """
    Декоратор для защиты путей к страницам.

    Обрабатывает:
        - Пустой путь → index.html
        - Directory traversal (..) → 404.html
        - Неизвестные страницы → 404.html
    """

    @wraps(func)
    def wrapper(name: str, *args, **kwargs):
        while "//" in name:
            name = name.replace("//", "/")
        # Очистка пути
        if name.startswith("/"):
            name = name[1:]

        # Пустой путь
        if not name:
            name = "index.html"

        # Защита от directory traversal
        if ".." in name or name.startswith("/"):
            name = "404.html"

        # Проверка на разрешенные файлы
        if name not in PAGE_FILES:
            name = "404.html"

        return func(name, *args, **kwargs)

    return wrapper


def _read_file(name: str) -> str:
    """Внутренняя функция: читает файл без проверки."""
    with open(os.path.join(PAGES_DIR, name), "r", encoding="utf-8") as fh:
        return fh.read()

@path_guard
def read_page(name: str) -> str:
    """
    Читает HTML-файл из директории pages.

    Аргументы:
        name (str): Имя запрашиваемого файла (например, 'index.html').

    Возвращает:
        str: Содержимое HTML-файла в виде строки.
    """
    return _read_file(name)




class Handler(BaseHTTPRequestHandler):
    """
    Обработчик HTTP-запросов для простого веб-сервера.

    Обрабатывает GET- и POST-запросы, обслуживает статические файлы
    и HTML-страницы из директорий static и pages соответственно.

    Атрибуты:
        - Поддерживает раздачу статики (CSS, JS, шрифты).
        - Возвращает HTML с корректным Content-Type.
        - Обрабатывает ошибки 404 и 500.
        - Принимает POST-данные и выводит их в консоль.
    """
    def _send(self, code: int, body: bytes, content_type: str) -> None:
        """
        Отправляет HTTP-ответ с указанным кодом, телом и типом контента.

        Аргументы:
            code (int): HTTP-статус ответа (например, 200, 404).
            body (bytes): Тело ответа в байтовом формате.
            content_type (str): MIME-тип содержимого (например, 'text/html').

        Возвращает:
            None
        """
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, code: int, html: str) -> None:
        """
        Отправляет HTML-ответ с корректным Content-Type.

        Аргументы:
            code (int): HTTP-статус ответа.
            html (str): HTML-содержимое в виде строки.

        Возвращает:
            None
        """
        self._send(code, html.encode("utf-8"), "text/html; charset=utf-8")

    def _send_static(self, file_path: str) -> None:
        """
        Отправляет статический файл с правильным MIME-типом.

        Аргументы:
            file_path (str): Полный путь к файлу на диске.

        Возвращает:
            None

        Примечания:
            - MIME-тип определяется по расширению файла.
            - Для CSS, JS, WOFF, WOFF2 используются предопределённые типы.
            - Файл читается в бинарном режиме.
        """
        ext = os.path.splitext(file_path)[1].lower()
        content_type = EXTRA_MIME.get(ext) or mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        with open(file_path, "rb") as fh:
            self._send(200, fh.read(), content_type)

    def _normalize_path(self, full_path: str) -> tuple[str, str]:
        """
        Нормализует путь, сохраняя GET-параметры.

        Аргументы:
            full_path (str): Полный путь с параметрами.

        Возвращает:
            tuple[str, str]: (нормализованный_путь, параметры)

        Пример:
            "///////?page=1" → ("/", "?page=1")
            "/contacts.html?success=true" → ("/contacts.html", "?success=true")
        """
        # Разделяем путь и параметры
        if "?" in full_path:
            path, query = full_path.split("?", 1)
            query = "?" + query
        else:
            path = full_path
            query = ""

        # Декодируем URL: %2E%2E -> ..
        path = unquote(path)

        # Для URL считаем и /, и \ разделителями.
        path = path.replace("\\", "/")

        # Нормализация . / .. / //
        path = posixpath.normpath(path)

        # URL должен начинаться с /
        if not path.startswith("/"):
            path = "/" + path

        # normpath("/") уже вернёт "/"
        return path, query

    def do_GET(self) -> None:
        """
        Обрабатывает входящие GET-запросы.

        Логика обработки:
            1. Если путь начинается с '/static/' → пытается отдать статический файл.
            2. Если путь '/404' или '/500' → возвращает соответствующую страницу ошибки.
            3. В остальных случаях → возвращает запрошенную HTML-страницу.

        Возвращает:
            None

        Примечания:
            - Все ошибки (FileNotFoundError, Exception) обрабатываются
              и возвращают страницы 404 или 500.
            - В консоль выводится каждый GET-запрос для отладки.
        """
        # Нормализуем путь с сохранением параметров
        normalized_path, query = self._normalize_path(self.path)
        # Если путь изменился — редирект с сохранением параметров
        if normalized_path != self.path.split("?")[0]:
            self.send_response(301)
            self.send_header("Location", normalized_path + query)
            self.end_headers()
            return

        # Основная логика (используем normalized_path)
        path = normalized_path

        if path.startswith("/static/"):
            real = os.path.abspath(os.path.join(STATIC_DIR, path[len("/static/") :]))
            print(f"[STATIC] URL: {path}")
            print(f"[STATIC] FILE: {real}")
            print(f"[STATIC] EXISTS: {os.path.isfile(real)}")
            if real.startswith(STATIC_DIR + os.sep) and os.path.isfile(real):
                self._send_static(real)
            else:
                self._send_html(404, _read_file("404.html"))
            return
        try:
            # страницы ошибок
            if path == "/404" or path == "/404.html":
                self._send_html(404, _read_file("404.html"))
            elif path == "/500" or path == "/500.html":
                self._send_html(500, _read_file("500.html"))
            else:
                self._send_html(200, read_page(path))
        except FileNotFoundError as exc:
            print("Файл не найден:", exc)
            self._send_html(404, _read_file("404.html"))
        except Exception as exc:
            print("Ошибка сервера:", exc)
            self._send_html(500, _read_file("500.html"))

    def do_POST(self) -> None:
        """
        Обрабатывает входящие POST-запросы.

        Логика обработки:
            1. Читает тело запроса.
            2. Парсит данные из формата application/x-www-form-urlencoded.
            3. Выводит полученные данные в консоль.
            4. Возвращает страницу 'contacts.html' или сообщение об успехе.

        Возвращает:
            None

        Примечания:
            - Данные выводятся в консоль для отладки в формате:
              ключ = значение1, значение2
            - В случае ошибки возвращается простое HTML-сообщение.
        """
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8")
        print(f"[POST] {self.path}, сырые данные: {raw}")
        print("Приняты данные от пользователя:")
        for key, values in parse_qs(raw).items():
            print(f"  {key} = {', '.join(values)}")
        try:
            self._send_html(200, read_page("contacts.html"))
        except Exception:
            self._send_html(500, _read_file("500.html"))

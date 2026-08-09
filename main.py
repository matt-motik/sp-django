from http.server import ThreadingHTTPServer

from src.server import Handler


def main():
    # sync_pages()
    server = ThreadingHTTPServer(("0.0.0.0", 8000), Handler)
    print("Сервер запущен: http://127.0.0.1:8000/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
        server.server_close()

if __name__ == "__main__":
    main()
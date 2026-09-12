import http.server
import socketserver
import os
import urllib.parse
from pathlib import Path

PORT = int(os.environ.get("PORT", 3000))
ROOT = Path(__file__).parent.resolve()

MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css":  "text/css; charset=utf-8",
    ".js":   "application/javascript; charset=utf-8",
    ".json": "application/json",
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif":  "image/gif",
    ".svg":  "image/svg+xml",
    ".ico":  "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf":  "font/ttf",
    ".mp3":  "audio/mpeg",
    ".wav":  "audio/wav",
}


class GameHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def guess_type(self, path):
        ext = Path(path).suffix.lower()
        return MIME_TYPES.get(ext, "application/octet-stream")

    def do_GET(self):
        # Убираем query string
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Главная страница
        if path in ("/", ""):
            path = "/index.html"

        # Защита от path traversal
        try:
            file_path = (ROOT / path.lstrip("/")).resolve()
            if not str(file_path).startswith(str(ROOT)):
                self.send_error(403, "Forbidden")
                return
        except Exception:
            self.send_error(400, "Bad Request")
            return

        # Если файла нет — красивая 404
        if not file_path.is_file():
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>404</title>
  <style>
    body {
      background: #0f0f13;
      color: #e0e0e0;
      font-family: system-ui, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      margin: 0;
    }
    h1 { color: #00ff9d; }
    a { color: #00b4ff; }
  </style>
</head>
<body>
  <div style="text-align:center">
    <h1>404</h1>
    <p>Страница не найдена</p>
    <a href="/">← На главную</a>
  </div>
</body>
</html>""".encode("utf-8"))
            return

        # Отдаём файл
        self.path = path
        return super().do_GET()

    def log_message(self, format, *args):
        # Красивый лог
        print(f"  {self.address_string()} → {format % args}")


def main():
    with socketserver.TCPServer(("", PORT), GameHandler) as httpd:
        print()
        print("  🎮  HTML Games Platform")
        print("  ─────────────────────")
        print(f"  Сервер запущен: http://localhost:{PORT}")
        print("  Нажми Ctrl+C чтобы остановить")
        print()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Сервер остановлен.")


if __name__ == "__main__":
    main()

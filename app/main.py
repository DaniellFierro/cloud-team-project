"""Минимальный HTTP-проект для учебных работ по облачным технологиям."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import json
import os

DATA_FILE = Path(__file__).with_name("services.json")


class Handler(BaseHTTPRequestHandler):
    def send_body(self, status, data, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/health":
            payload = json.dumps({"status": "ok"}, ensure_ascii=False).encode("utf-8")
            self.send_body(200, payload, "application/json; charset=utf-8")
        elif path == "/api/services":
            payload = DATA_FILE.read_bytes()
            self.send_body(200, payload, "application/json; charset=utf-8")
        elif path == "/":
            title = os.environ.get("APP_TITLE", "Cloud Service Catalog")
            import html
            safe_title = html.escape(title, quote=True)
            page = (f"<!doctype html><html lang='ru'><meta charset='utf-8'>"
                    f"<title>{safe_title}</title><h1>{safe_title}</h1>"
                    "<p>Доступные API: <a href='/api/services'>/api/services</a>, "
                    "<a href='/health'>/health</a>.</p></html>")
            self.send_body(200, page.encode("utf-8"), "text/html; charset=utf-8")
        else:
            self.send_body(404, b'{"error":"not found"}', "application/json; charset=utf-8")


def make_server(host="0.0.0.0", port=5000):
    return ThreadingHTTPServer((host, int(port)), Handler)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    host = os.environ.get("HOST", "0.0.0.0")
    with make_server(host=host, port=port) as server:
        print(f"Serving on http://{host}:{port}", flush=True)
        server.serve_forever()

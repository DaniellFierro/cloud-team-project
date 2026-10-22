"""Автоматическая проверка HTTP-маршрутов без сторонних пакетов."""
import json
import threading
import unittest
import os
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import urlopen
from app.main import make_server


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(host="127.0.0.1", port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_health(self):
        with urlopen(self.base + "/health") as r:
            self.assertEqual(200, r.status)
            self.assertEqual("ok", json.load(r)["status"])

    def test_catalog(self):
        with urlopen(self.base + "/api/services") as r:
            models = {item["model"] for item in json.load(r)["services"]}
            self.assertEqual({"IaaS", "PaaS", "SaaS"}, models)

    def test_home(self):
        with urlopen(self.base + "/") as r:
            self.assertIn("Cloud Service Catalog", r.read().decode("utf-8"))

    def test_unknown_route(self):
        with self.assertRaises(HTTPError) as caught:
            urlopen(self.base + "/missing", timeout=5)
        self.assertEqual(404, caught.exception.code)
        self.assertEqual({"error": "not found"}, json.load(caught.exception))

    def test_query_string(self):
        with urlopen(self.base + "/health?probe=1", timeout=5) as r:
            self.assertEqual("ok", json.load(r)["status"])

    def test_html_escape_and_headers(self):
        with patch.dict(os.environ, {"APP_TITLE": "<script>alert('x')</script>"}):
            with urlopen(self.base + "/", timeout=5) as r:
                body = r.read()
                self.assertNotIn(b"<script>", body)
                self.assertIn(b"&lt;script&gt;", body)
                self.assertEqual("nosniff", r.headers["X-Content-Type-Options"])
                self.assertEqual(len(body), int(r.headers["Content-Length"]))


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Local preview with the same clean-URL and redirect behavior as .htaccess."""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent / "public"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._serve()

    def do_HEAD(self):
        self._serve(head=True)

    def _serve(self, head=False):
        split = urlsplit(self.path)
        path = unquote(split.path)
        query = ("?" + split.query) if split.query else ""

        if path.rstrip("/") in ("/index.html",):
            self._redirect("/" + query)
            return
        if path.endswith(".html") and path != "/404.html":
            self._redirect(path[:-5].rstrip("/") + "/" + query)
            return
        if path.rstrip("/") in ("/site/394d9953",):
            self._redirect("/" + query)
            return
        if path.startswith("/site/394d9953/"):
            rest = path[len("/site/394d9953/"):].strip("/")
            dest = ("/" + rest + "/") if rest else "/"
            self._redirect(dest + query)
            return
        stripped = path.lstrip("/")
        if stripped.startswith("\u200bresidential-electrical-services"):
            self._redirect("/residential-electrical-services/" + query)
            return

        target = self._file(path)
        if target is None:
            target = ROOT / "404.html"
            data = target.read_bytes()
            self.send_response(404)
            self._headers(target, len(data))
            if not head:
                self.wfile.write(data)
            return
        data = target.read_bytes()
        self.send_response(200)
        self._headers(target, len(data))
        if not head:
            self.wfile.write(data)

    def _file(self, path):
        if path.endswith("/"):
            candidate = ROOT / path.lstrip("/") / "index.html"
        else:
            candidate = ROOT / path.lstrip("/")
            if candidate.is_dir():
                candidate = candidate / "index.html"
        if candidate.is_file():
            return candidate
        return None

    def _redirect(self, location):
        self.send_response(301)
        self.send_header("Location", location or "/")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _headers(self, path, length):
        kind = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".xml": "application/xml",
            ".txt": "text/plain; charset=utf-8",
            ".webp": "image/webp",
            ".png": "image/png",
            ".svg": "image/svg+xml",
        }.get(path.suffix, "application/octet-stream")
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(length))
        self.end_headers()

    def log_message(self, fmt, *args):
        return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    if not (ROOT / "index.html").is_file():
        raise SystemExit("public/index.html is missing. Run python3 build/build.py first.")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Serving {ROOT} at http://127.0.0.1:{args.port}/")
    server.serve_forever()


if __name__ == "__main__":
    main()

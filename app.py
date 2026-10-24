#!/usr/bin/env python3
"""Loopback-only server for the Rural Signal contest edition."""

from __future__ import annotations

import argparse
import json
import mimetypes
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import engine


ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
CASES = {case["id"]: case for case in engine.load_fixtures()}
MODEL_LOCK = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, value: object) -> None:
        self._send(status, "application/json; charset=utf-8", json.dumps(value).encode())

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/cases":
            payload = []
            for case in CASES.values():
                saved = engine.RESULTS / f"{case['id']}.json"
                result = json.loads(saved.read_text(encoding="utf-8")) if saved.is_file() else None
                payload.append({
                    "id": case["id"], "title": case["title"], "eyebrow": case["eyebrow"],
                    "raw_notice": case["raw_notice"], "locked": case["locked"], "result": result,
                })
            self._json(200, payload)
            return
        relative = "index.html" if path == "/" else path.removeprefix("/")
        target = (STATIC / relative).resolve()
        if STATIC not in target.parents or not target.is_file():
            self._send(404, "text/plain; charset=utf-8", b"Not found")
            return
        mime = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self._send(200, f"{mime}; charset=utf-8" if mime.startswith("text/") else mime, target.read_bytes())

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/run":
            self._json(404, {"error": "Not found"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 1024:
                raise ValueError("Invalid request size")
            request = json.loads(self.rfile.read(size))
            if set(request) != {"case_id"} or request["case_id"] not in CASES:
                raise ValueError("Choose a bundled demonstration case")
            with MODEL_LOCK:
                result = engine.run_case(CASES[request["case_id"]])
            if not result["passed"]:
                self._json(422, {"error": "Safety validation failed; output withheld", "details": result["errors"]})
                return
            self._json(200, result)
        except (ValueError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)[:240]})
        except Exception as exc:
            self._json(500, {"error": str(exc)[:240]})

    def log_message(self, fmt: str, *args: object) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    print(f"Rural Signal contest edition: http://{args.host}:{args.port}", flush=True)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()

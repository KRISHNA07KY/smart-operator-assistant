"""backend/app.py
Local lightweight HTTP server for serving the Smart Operator Assistant UI
and handling dummy / real ML prediction endpoints.
"""
import os
import json
import mimetypes
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from typing import Tuple
from backend.dummy_ml import predict_safety, predict_task_time, detect_anomalies

import sys

if getattr(sys, 'frozen', False):
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    STATIC_DIR = os.path.abspath(os.path.join(base_dir, "frontend", "dist"))
    if not os.path.exists(STATIC_DIR):
        STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.executable), "frontend", "dist"))
else:
    STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

class CatAppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            self._send_json(200, {"status": "ok", "app": "CAT Smart Operator Assistant", "backend": "Python Qt Backend"})
            return
        
        # If file doesn't exist, serve index.html (SPA client-side routing)
        requested_file = os.path.join(STATIC_DIR, self.path.lstrip("/").split("?")[0])
        if not os.path.exists(requested_file) and not self.path.startswith("/api/"):
            index_path = os.path.join(STATIC_DIR, "index.html")
            if os.path.exists(index_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                with open(index_path, "rb") as f:
                    content = f.read()
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        return super().do_GET()

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len > 0 else b"{}"
        try:
            data = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            data = {}

        if self.path == "/api/predict/safety":
            res = predict_safety(data.get("inputs", data), data.get("context"))
            self._send_json(200, res)
        elif self.path == "/api/predict/task-time":
            res = predict_task_time(data)
            self._send_json(200, res)
        elif self.path == "/api/analyze/anomalies":
            op_id = data.get("operator_id", "OP-1001")
            res = detect_anomalies(op_id, data.get("session", data))
            self._send_json(200, res)
        else:
            self._send_json(404, {"error": "Not Found", "path": self.path})

    def _send_json(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Silence routine static asset logs
        return


def start_server(port: int = 5173, host: str = "127.0.0.1") -> Tuple[ThreadingHTTPServer, int]:
    """Starts the HTTP server on an available port, defaulting to 5173."""
    server = None
    actual_port = port
    for p in range(port, port + 20):
        try:
            server = ThreadingHTTPServer((host, p), CatAppHandler)
            actual_port = p
            break
        except OSError:
            continue
    if server is None:
        raise RuntimeError("Failed to bind local CAT dashboard server to any port.")
    return server, actual_port

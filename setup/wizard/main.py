"""Setup Wizard - Local web server that serves the setup wizard UI.

Starts an HTTP server on a free port and opens the default browser.
The wizard UI runs in the browser and communicates with this server via
JSON API calls to perform installations and configuration.
"""

import http.server
from http.server import ThreadingHTTPServer
import json
import os
import socket
import sys
import threading
import webbrowser

# Ensure the setup package is importable
WIZARD_DIR = os.path.dirname(os.path.abspath(__file__))
SETUP_DIR = os.path.dirname(WIZARD_DIR)
PROJECT_ROOT = os.path.dirname(SETUP_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from setup.wizard.api import handle_api, set_shutdown_callback

WEB_DIR = os.path.join(WIZARD_DIR, "web")


class WizardHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that serves static files and API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._handle_api_get()
        else:
            # Serve static files from web/
            if self.path == "/":
                self.path = "/index.html"
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self._handle_api_post()
        else:
            self.send_error(404)

    def _handle_api_get(self):
        result = handle_api(self.path)
        self._send_json(result)

    def _handle_api_post(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = None
        if content_length > 0:
            raw = self.rfile.read(content_length)
            body = json.loads(raw.decode("utf-8"))
        result = handle_api(self.path, body)
        self._send_json(result)

    def _send_json(self, data):
        response = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response)

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        """Suppress default request logging to keep output clean."""
        pass


def find_free_port():
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def main():
    port = find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), WizardHandler)

    # Register shutdown callback so the API can stop the server
    def shutdown():
        threading.Thread(target=server.shutdown, daemon=True).start()

    set_shutdown_callback(shutdown)

    url = f"http://127.0.0.1:{port}"
    print(f"Setup wizard running at {url}")
    print("Opening browser...")
    print("(Close the browser tab or press Ctrl+C to exit)")

    # Open browser in a separate thread to avoid blocking
    threading.Thread(target=lambda: webbrowser.open(url), daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down wizard server.")
        server.shutdown()


if __name__ == "__main__":
    main()

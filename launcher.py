"""
OtoServis Desktop Launcher — PyWebView entry point.

Starts the FastAPI application in a background thread
and opens it inside a native PyWebView window.
"""

import sys
import time
import socket
import signal
import logging
import threading
from urllib.request import urlopen

import uvicorn

logger = logging.getLogger("launcher")


def find_free_port() -> int:
    """Find an available TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class UvicornServer:
    """Manages the uvicorn server lifecycle in a background thread."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        config = uvicorn.Config(
            "app.main:app",
            host=self.host,
            port=self.port,
            log_level="warning",
            access_log=False,
        )
        self.server = uvicorn.Server(config)
        self.thread = threading.Thread(target=self.server.run, daemon=True)
        self.thread.start()

    def wait_until_ready(self, timeout: float = 15.0):
        """Block until the server responds or timeout."""
        url = f"http://{self.host}:{self.port}/auth/login"
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                urlopen(url, timeout=1)
                return True
            except Exception:
                time.sleep(0.3)
        return False

    def stop(self):
        if self.server:
            self.server.should_exit = True
        if self.thread:
            self.thread.join(timeout=5)


def launch_webview(url: str):
    """Open a native desktop window using pywebview."""
    try:
        import webview

        window = webview.create_window(
            title="Oto Servis Yönetim Sistemi",
            url=url,
            width=1280,
            height=800,
            min_size=(1024, 600),
            text_select=True,
        )
        webview.start()
    except ImportError:
        logger.warning("pywebview not installed, falling back to system browser.")
        import webbrowser
        webbrowser.open(url)
        # Keep main thread alive so server doesn't die
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    except Exception as e:
        logger.error(f"PyWebView failed: {e}. Falling back to system browser.")
        import webbrowser
        webbrowser.open(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


def main():
    port = find_free_port()
    logger.info(f"Starting OtoServis on port {port}...")

    server = UvicornServer(port=port)
    server.start()

    if not server.wait_until_ready():
        logger.error("Server failed to start within timeout.")
        sys.exit(1)

    url = f"http://127.0.0.1:{port}"
    logger.info(f"Server ready at {url}")

    try:
        launch_webview(url)
    finally:
        logger.info("Shutting down server...")
        server.stop()
        logger.info("Goodbye.")


if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    main()

"""
OtoServis Desktop Launcher — PyWebView entry point.

Starts the FastAPI application in a background thread
and opens it inside a native PyWebView window.

Single-instance: only one server runs at a time.
A second launch detects the existing server and opens it
in the default browser instead of starting a duplicate.
"""

import sys
import os
import time
import socket
import signal
import logging
import threading
import atexit
import tempfile
from urllib.request import urlopen

import uvicorn

# ── PyInstaller: fix working directory & module path ──────────
if getattr(sys, 'frozen', False):
    # When running as a bundled exe, set the working directory
    # to the directory containing the exe
    os.chdir(os.path.dirname(sys.executable))
    # Ensure the temp extraction dir is on the path
    bundle_dir = sys._MEIPASS
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)

# ── Logging setup (visible even without console) ─────────────
log_dir = os.path.join(tempfile.gettempdir(), "OtoServisLogs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "launcher.log")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("launcher")
logger.info(f"Launcher started. Log file: {log_file}")
logger.info(f"Python: {sys.version}")
logger.info(f"Frozen: {getattr(sys, 'frozen', False)}")
if getattr(sys, 'frozen', False):
    logger.info(f"Bundle dir: {sys._MEIPASS}")
    logger.info(f"Executable: {sys.executable}")

# ── Single-instance lock ────────────────────────────────────────
LOCK_FILE = os.path.join(tempfile.gettempdir(), "otoservis_pro.lock")


def _is_server_alive(port: int, timeout: float = 1.0) -> bool:
    """Check whether a server is actually responding on the given port."""
    try:
        urlopen(f"http://127.0.0.1:{port}/auth/login", timeout=timeout)
        return True
    except Exception:
        return False


def _read_lock() -> int | None:
    """Read the port from the lock file, or None if absent / stale."""
    try:
        with open(LOCK_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def _write_lock(port: int):
    """Write the port to the lock file."""
    with open(LOCK_FILE, "w") as f:
        f.write(str(port))


def _remove_lock():
    """Delete the lock file."""
    try:
        os.remove(LOCK_FILE)
    except OSError:
        pass


def _check_single_instance() -> bool:
    """Return True if another instance is already running and was activated.

    If an old lock file exists but the server is dead, the stale lock is
    cleaned up and we return False so a fresh server can start.
    """
    existing_port = _read_lock()
    if existing_port is None:
        return False

    if _is_server_alive(existing_port):
        # Another instance is running → open it in the browser and quit
        url = f"http://127.0.0.1:{existing_port}"
        logger.info(f"OtoServis is already running at {url}. Opening in browser…")
        import webbrowser
        webbrowser.open(url)
        return True

    # Stale lock file (server crashed / was killed) → clean up
    logger.info("Stale lock file found, removing…")
    _remove_lock()
    return False
# ────────────────────────────────────────────────────────────────


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

        logger.info("Creating PyWebView window...")

        window = webview.create_window(
            title="Oto Servis Yönetim Sistemi",
            url=url,
            width=1280,
            height=800,
            min_size=(1024, 600),
            text_select=True,
        )

        # Choose GUI backend based on platform
        if sys.platform == "win32":
            gui_backend = "edgechromium"
        else:
            gui_backend = "gtk"

        logger.info(f"Starting PyWebView with gui={gui_backend}")
        webview.start(gui=gui_backend)

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
        logger.error(f"PyWebView failed: {e}. Falling back to system browser.", exc_info=True)
        import webbrowser
        webbrowser.open(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


def main():
    # ── Single-instance guard ──
    if _check_single_instance():
        sys.exit(0)

    port = find_free_port()
    logger.info(f"Starting OtoServis on port {port}...")

    # Write lock file so other launches know we're running
    _write_lock(port)
    atexit.register(_remove_lock)

    server = UvicornServer(port=port)
    server.start()

    if not server.wait_until_ready():
        logger.error("Server failed to start within timeout.")
        _remove_lock()
        sys.exit(1)

    url = f"http://127.0.0.1:{port}"
    logger.info(f"Server ready at {url}")

    try:
        launch_webview(url)
    finally:
        logger.info("Shutting down server...")
        server.stop()
        _remove_lock()
        logger.info("Goodbye.")


if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    main()

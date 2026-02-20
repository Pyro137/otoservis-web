"""
Application settings with platform-aware AppData paths.

- On Windows: %APPDATA%/OtoServisApp/
- On Linux:   ~/.local/share/OtoServisApp/
"""

import os
import sys
import secrets
import logging
import logging.handlers
import configparser
from pathlib import Path
from pydantic_settings import BaseSettings


def _get_app_data_dir() -> Path:
    """Return the platform-appropriate application data directory."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "OtoServisApp"


def _get_or_create_secret_key(app_data_dir: Path) -> str:
    """Load SECRET_KEY from config.ini or generate one and persist it."""
    config_file = app_data_dir / "config.ini"
    cp = configparser.ConfigParser()

    if config_file.exists():
        cp.read(config_file, encoding="utf-8")
        key = cp.get("security", "secret_key", fallback=None)
        if key:
            return key

    # Generate and persist
    key = secrets.token_hex(32)
    if not cp.has_section("security"):
        cp.add_section("security")
    cp.set("security", "secret_key", key)

    # Ensure defaults section exists
    if not cp.has_section("company"):
        cp.add_section("company")
        cp.set("company", "name", "OtoServis Pro")
        cp.set("company", "currency", "TRY")
        cp.set("company", "vat_rate", "20.0")

    os.makedirs(app_data_dir, exist_ok=True)
    with open(config_file, "w", encoding="utf-8") as f:
        cp.write(f)

    return key


# ── Resolve paths ──
APP_DATA_DIR = _get_app_data_dir()


def _get_base_dir() -> Path:
    """Return the base directory — handles PyInstaller bundles correctly."""
    if getattr(sys, 'frozen', False):
        # Running inside PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running normally (development)
        return Path(__file__).resolve().parent.parent.parent


PROJECT_DIR = _get_base_dir()


class Settings(BaseSettings):
    # App
    APP_NAME: str = "OtoServis Pro"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database — stored in AppData, NOT inside the project folder
    APP_DATA_DIR: Path = APP_DATA_DIR
    DATABASE_URL: str = f"sqlite:///{APP_DATA_DIR / 'otoservis.db'}"

    # Security — unique per installation
    SECRET_KEY: str = _get_or_create_secret_key(APP_DATA_DIR)
    SESSION_MAX_AGE: int = 3600 * 8  # 8 hours

    # VAT
    DEFAULT_VAT_RATE: float = 20.0

    # Paths
    BASE_DIR: Path = PROJECT_DIR
    BACKUP_DIR: Path = APP_DATA_DIR / "backups"
    LOG_DIR: Path = APP_DATA_DIR / "logs"
    STATIC_DIR: Path = _get_base_dir() / "app" / "static"
    TEMPLATE_DIR: Path = _get_base_dir() / "app" / "templates"

    # Backup
    MAX_BACKUP_COUNT: int = 30

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# ── Ensure directories exist ──
for d in [settings.BACKUP_DIR, settings.LOG_DIR, settings.APP_DATA_DIR]:
    os.makedirs(d, exist_ok=True)


# ── Centralized Logging ──
def setup_logging():
    """Configure file + console logging."""
    log_file = settings.LOG_DIR / "otoservis.log"
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.handlers.RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        ),
    ]

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )

    # Silence noisy loggers in production
    if not settings.DEBUG:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


setup_logging()

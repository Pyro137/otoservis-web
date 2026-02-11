import shutil
import os
from datetime import datetime
from pathlib import Path
from app.core.config import settings


class BackupService:
    @staticmethod
    def create_backup() -> str:
        """Create a timestamped backup of the SQLite database."""
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        if not os.path.exists(db_path):
            raise FileNotFoundError("Veritabanı dosyası bulunamadı.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"otoservis_backup_{timestamp}.db"
        backup_path = settings.BACKUP_DIR / backup_filename

        shutil.copy2(db_path, backup_path)
        return str(backup_path)

    @staticmethod
    def get_backups() -> list:
        """List all available backups."""
        backups = []
        if settings.BACKUP_DIR.exists():
            for f in sorted(settings.BACKUP_DIR.glob("*.db"), reverse=True):
                stat = f.stat()
                backups.append({
                    "filename": f.name,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created": datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M"),
                })
        return backups

    @staticmethod
    def restore_backup(filename: str) -> bool:
        """Restore the database from a backup file."""
        backup_path = settings.BACKUP_DIR / filename
        if not backup_path.exists():
            raise FileNotFoundError("Yedek dosyası bulunamadı.")

        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        # Create a pre-restore backup
        pre_restore = settings.BACKUP_DIR / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_path, pre_restore)
        # Restore
        shutil.copy2(backup_path, db_path)
        return True

    @staticmethod
    def cleanup_old_backups():
        """Remove oldest backups if exceeding MAX_BACKUP_COUNT."""
        if settings.BACKUP_DIR.exists():
            backups = sorted(settings.BACKUP_DIR.glob("*.db"))
            while len(backups) > settings.MAX_BACKUP_COUNT:
                oldest = backups.pop(0)
                oldest.unlink()

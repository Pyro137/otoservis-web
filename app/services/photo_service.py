import os
import uuid
import logging
from typing import List, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.work_order_photo import WorkOrderPhoto
from app.repositories.work_order_photo_repo import WorkOrderPhotoRepository
from app.core.config import settings

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def get_upload_dir(work_order_id: int) -> Path:
    """Return the upload directory for a given work order."""
    upload_dir = settings.STATIC_DIR / "uploads" / "work_orders" / str(work_order_id)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


class PhotoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = WorkOrderPhotoRepository(db)

    def get_by_work_order(self, work_order_id: int) -> List[WorkOrderPhoto]:
        return self.repo.get_by_work_order(work_order_id)

    def get_by_id(self, photo_id: int) -> Optional[WorkOrderPhoto]:
        return self.repo.get_by_id(photo_id)

    async def upload_photo(
        self,
        work_order_id: int,
        file: UploadFile,
        category: str,
        caption: str = None,
        user_id: int = None,
    ) -> Optional[WorkOrderPhoto]:
        """Validate and save an uploaded photo."""
        # Validate extension
        original_name = file.filename or "photo.jpg"
        ext = os.path.splitext(original_name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Desteklenmeyen dosya türü: {ext}. Sadece JPG, PNG, WEBP desteklenir.")

        # Read file and validate size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise ValueError("Dosya boyutu 10 MB'ı aşamaz.")

        # Generate unique filename
        unique_name = f"{uuid.uuid4().hex}{ext}"
        upload_dir = get_upload_dir(work_order_id)
        file_path = upload_dir / unique_name

        # Save to disk
        with open(file_path, "wb") as f:
            f.write(contents)

        logger.info(f"Photo uploaded: {file_path} ({len(contents)} bytes)")

        # Save to database
        photo_data = {
            "work_order_id": work_order_id,
            "filename": unique_name,
            "original_filename": original_name,
            "category": category,
            "caption": caption or None,
            "uploaded_by": user_id,
        }
        return self.repo.create(photo_data)

    def delete_photo(self, photo_id: int) -> bool:
        """Delete a photo from disk and database."""
        photo = self.repo.get_by_id(photo_id)
        if not photo:
            return False

        # Delete file from disk
        file_path = get_upload_dir(photo.work_order_id) / photo.filename
        if file_path.exists():
            os.remove(file_path)
            logger.info(f"Photo deleted from disk: {file_path}")

        # Delete from database
        self.repo.hard_delete(photo)
        return True

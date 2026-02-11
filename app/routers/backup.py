from fastapi import APIRouter, Request, Depends, UploadFile, File
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.utils.backup_service import BackupService

router = APIRouter(prefix="/backup", tags=["backup"])


@router.get("/")
async def backup_page(
    request: Request,
    user=Depends(require_admin),
):
    backups = BackupService.get_backups()
    return request.app.state.templates.TemplateResponse(
        "backup/index.html",
        {"request": request, "user": user, "backups": backups},
    )


@router.post("/create")
async def create_backup(
    request: Request,
    user=Depends(require_admin),
):
    try:
        path = BackupService.create_backup()
        BackupService.cleanup_old_backups()
    except Exception as e:
        pass
    return RedirectResponse("/backup", status_code=303)


@router.post("/upload")
async def upload_backup(
    request: Request,
    backup_file: UploadFile = File(...),
    user=Depends(require_admin),
):
    try:
        content = await backup_file.read()
        BackupService.import_backup(content, backup_file.filename)
    except Exception as e:
        pass
    return RedirectResponse("/backup", status_code=303)


@router.post("/restore/{filename}")
async def restore_backup(
    filename: str,
    request: Request,
    user=Depends(require_admin),
):
    try:
        BackupService.restore_backup(filename)
    except Exception as e:
        pass
    return RedirectResponse("/backup", status_code=303)

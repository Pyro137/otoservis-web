from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.part import Part
from app.repositories.part_repo import PartRepository
from app.repositories.audit_log_repo import AuditLogRepository
from app.core.enums import AuditAction


class PartService:
    def __init__(self, db: Session):
        self.repo = PartRepository(db)
        self.audit = AuditLogRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Part]:
        return self.repo.get_all_active(skip=skip, limit=limit)

    def count(self) -> int:
        return self.repo.count()

    def get_by_id(self, part_id: int) -> Optional[Part]:
        return self.repo.get_by_id(part_id)

    def search(self, query: str) -> List[Part]:
        return self.repo.search(query)

    def get_low_stock(self) -> List[Part]:
        return self.repo.get_low_stock()

    def create(self, data: dict, user_id: int = None) -> Part:
        part = self.repo.create(data)
        if user_id:
            self.audit.log(user_id, "Part", part.id, AuditAction.CREATE, data)
        return part

    def update(self, part_id: int, data: dict, user_id: int = None) -> Optional[Part]:
        part = self.repo.get_by_id(part_id)
        if not part:
            return None
        changes = {}
        for key, value in data.items():
            old_val = getattr(part, key, None)
            if str(old_val) != str(value):
                changes[key] = {"old": str(old_val), "new": str(value)}
        part = self.repo.update(part, data)
        if user_id and changes:
            self.audit.log(user_id, "Part", part.id, AuditAction.UPDATE, changes)
        return part

    def delete(self, part_id: int, user_id: int = None) -> bool:
        part = self.repo.get_by_id(part_id)
        if not part:
            return False
        self.repo.update(part, {"is_active": False})
        if user_id:
            self.audit.log(user_id, "Part", part_id, AuditAction.DELETE)
        return True

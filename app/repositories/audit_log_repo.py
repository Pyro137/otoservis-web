import json
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.core.enums import AuditAction


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        user_id: int,
        entity_name: str,
        entity_id: int,
        action: AuditAction,
        changes: dict = None,
    ) -> AuditLog:
        audit = AuditLog(
            user_id=user_id,
            entity_name=entity_name,
            entity_id=entity_id,
            action=action,
            changes_json=json.dumps(changes, default=str) if changes else None,
        )
        self.db.add(audit)
        self.db.commit()
        return audit

    def get_for_entity(self, entity_name: str, entity_id: int):
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.entity_name == entity_name, AuditLog.entity_id == entity_id)
            .order_by(AuditLog.timestamp.desc())
            .all()
        )

    def get_recent(self, limit: int = 50):
        return (
            self.db.query(AuditLog)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )

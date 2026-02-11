from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SAEnum, func

from app.core.database import Base
from app.core.enums import AuditAction


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    entity_name = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False)
    action = Column(SAEnum(AuditAction), nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)
    changes_json = Column(Text, nullable=True)

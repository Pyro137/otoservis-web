from datetime import datetime

from sqlalchemy import Column, DateTime, Boolean, func


class TimestampMixin:
    """Mixin that adds created_at and updated_at columns."""
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class SoftDeleteMixin:
    """Mixin that adds soft delete support."""
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.enums import PhotoCategory
from app.models.base import TimestampMixin


class WorkOrderPhoto(Base, TimestampMixin):
    __tablename__ = "work_order_photos"

    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    category = Column(SAEnum(PhotoCategory), default=PhotoCategory.OTHER, nullable=False)
    caption = Column(Text, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    work_order = relationship("WorkOrder", backref="photos")
    uploader = relationship("User", foreign_keys=[uploaded_by])

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.enums import WorkOrderItemType
from app.models.base import TimestampMixin


class WorkOrderItem(Base, TimestampMixin):
    __tablename__ = "work_order_items"

    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, index=True)
    type = Column(SAEnum(WorkOrderItemType), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=True)

    description = Column(String(300), nullable=False)
    quantity = Column(Numeric(10, 2), default=1, nullable=False)
    unit_price = Column(Numeric(12, 2), default=0, nullable=False)
    discount = Column(Numeric(12, 2), default=0, nullable=False)
    vat_rate = Column(Numeric(5, 2), default=20, nullable=False)
    total_price = Column(Numeric(12, 2), default=0, nullable=False)

    # Relationships
    work_order = relationship("WorkOrder", back_populates="items")
    part = relationship("Part")

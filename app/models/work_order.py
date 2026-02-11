from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.enums import WorkOrderStatus
from app.models.base import TimestampMixin, SoftDeleteMixin


class WorkOrder(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    work_order_number = Column(String(20), unique=True, nullable=False, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    complaint_description = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    km_in = Column(Integer, nullable=True)
    km_out = Column(Integer, nullable=True)
    fuel_level = Column(String(20), nullable=True)

    status = Column(
        SAEnum(WorkOrderStatus),
        default=WorkOrderStatus.PENDING,
        nullable=False,
        index=True,
    )

    # Financial fields (Decimal)
    labor_total = Column(Numeric(12, 2), default=0, nullable=False)
    parts_total = Column(Numeric(12, 2), default=0, nullable=False)
    discount_total = Column(Numeric(12, 2), default=0, nullable=False)
    subtotal = Column(Numeric(12, 2), default=0, nullable=False)
    vat_rate = Column(Numeric(5, 2), default=20, nullable=False)
    vat_total = Column(Numeric(12, 2), default=0, nullable=False)
    grand_total = Column(Numeric(12, 2), default=0, nullable=False)

    completed_at = Column(DateTime, nullable=True)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="work_orders")
    customer = relationship("Customer", back_populates="work_orders")
    technician = relationship("User", foreign_keys=[technician_id])
    items = relationship("WorkOrderItem", back_populates="work_order", cascade="all, delete-orphan", lazy="selectin")
    payments = relationship("Payment", back_populates="work_order", lazy="selectin")
    invoice = relationship("Invoice", back_populates="work_order", uselist=False)

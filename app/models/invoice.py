from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, Enum as SAEnum, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.enums import PaymentStatus


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(30), unique=True, nullable=False, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), unique=True, nullable=False)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.UNPAID, nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)
    vat_total = Column(Numeric(12, 2), nullable=False)
    grand_total = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    work_order = relationship("WorkOrder", back_populates="invoice")

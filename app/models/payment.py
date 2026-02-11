from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SAEnum, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.enums import PaymentMethod


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(SAEnum(PaymentMethod), nullable=False)
    payment_date = Column(DateTime, default=func.now(), nullable=False)
    reference_number = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    work_order = relationship("WorkOrder", back_populates="payments")

from sqlalchemy import Column, Integer, String, Text, Numeric, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.enums import CustomerType
from app.models.base import TimestampMixin, SoftDeleteMixin


class Customer(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(SAEnum(CustomerType), default=CustomerType.INDIVIDUAL, nullable=False)
    full_name = Column(String(150), nullable=False)
    company_name = Column(String(200), nullable=True)
    tax_number = Column(String(20), nullable=True, index=True)
    tax_office = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=False, index=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    total_debt = Column(Numeric(12, 2), default=0, nullable=False)

    # Relationships
    vehicles = relationship("Vehicle", back_populates="customer", lazy="selectin")
    work_orders = relationship("WorkOrder", back_populates="customer", lazy="dynamic")

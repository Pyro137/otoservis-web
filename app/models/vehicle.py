from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.enums import FuelType, TransmissionType
from app.models.base import TimestampMixin, SoftDeleteMixin


class Vehicle(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    plate_number = Column(String(15), unique=True, nullable=False, index=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=True)
    fuel_type = Column(SAEnum(FuelType), nullable=True)
    transmission_type = Column(SAEnum(TransmissionType), nullable=True)
    chassis_number = Column(String(30), nullable=True, unique=True, index=True)
    engine_number = Column(String(30), nullable=True)
    current_km = Column(Integer, nullable=True)
    inspection_expiry_date = Column(Date, nullable=True)
    insurance_expiry_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="vehicles")
    work_orders = relationship("WorkOrder", back_populates="vehicle", lazy="dynamic")

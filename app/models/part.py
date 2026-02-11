from sqlalchemy import Column, Integer, String, Numeric, Boolean, CheckConstraint

from app.core.database import Base
from app.models.base import TimestampMixin


class Part(Base, TimestampMixin):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True, index=True)
    purchase_price = Column(Numeric(12, 2), default=0, nullable=False)
    sale_price = Column(Numeric(12, 2), default=0, nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)
    critical_level = Column(Integer, default=5, nullable=False)
    supplier_name = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        CheckConstraint("stock_quantity >= 0", name="ck_parts_stock_non_negative"),
    )

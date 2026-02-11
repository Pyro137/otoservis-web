from sqlalchemy import Column, Integer, String, Boolean, Enum as SAEnum

from app.core.database import Base
from app.core.enums import UserRole
from app.models.base import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.TECHNICIAN, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

from sqlalchemy import Column, String, DateTime, func, Integer, Boolean
from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), index=True, nullable=False)
    name = Column(String(64), nullable=False)
    color = Column(String(16), nullable=False)
    order = Column(Integer, default=0, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

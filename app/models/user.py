from sqlalchemy import Column, String, DateTime, func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

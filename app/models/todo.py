from sqlalchemy import Column, String, DateTime, func, Boolean, Date, JSON
from app.core.database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), index=True, nullable=False)
    title = Column(String(128), nullable=False)
    description = Column(String(512), nullable=True)
    priority = Column(String(16), nullable=False, default="medium")
    status = Column(String(16), nullable=False, default="todo")
    due_date = Column(Date, nullable=True)
    remind_at = Column(DateTime, nullable=True)
    category_id = Column(String(36), nullable=True)
    tags = Column(JSON, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

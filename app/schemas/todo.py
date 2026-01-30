from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    status: str = "todo"
    due_date: Optional[date] = None
    remind_at: Optional[datetime] = None
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    remind_at: Optional[datetime] = None
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None
    completed_at: Optional[datetime] = None


class TodoOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    priority: str
    status: str
    due_date: Optional[date] = None
    remind_at: Optional[datetime] = None
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TodoBatchStatus(BaseModel):
    ids: List[str]
    status: str

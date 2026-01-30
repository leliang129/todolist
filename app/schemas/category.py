from pydantic import BaseModel, ConfigDict
from typing import Optional


class CategoryCreate(BaseModel):
    name: str
    color: str
    order: Optional[int] = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    order: Optional[int] = None


class CategoryOut(BaseModel):
    id: str
    name: str
    color: str
    order: int
    is_system: bool

    model_config = ConfigDict(from_attributes=True)

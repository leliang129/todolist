from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: Optional[T] = None

    model_config = ConfigDict(from_attributes=True)


class Page(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int

    model_config = ConfigDict(from_attributes=True)

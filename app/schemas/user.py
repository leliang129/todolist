from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class UserOut(UserBase):
    id: str

    model_config = ConfigDict(from_attributes=True)

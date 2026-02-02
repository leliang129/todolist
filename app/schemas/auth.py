from pydantic import BaseModel, Field
from typing import Optional


class TokenOut(BaseModel):
    access_token: str
    expires_in: int
    user: dict


class LoginIn(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=72)


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=72)
    email: Optional[str] = None

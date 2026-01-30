from pydantic import BaseModel
from typing import Optional


class TokenOut(BaseModel):
    access_token: str
    expires_in: int
    user: dict


class LoginIn(BaseModel):
    username: str
    password: str


class RegisterIn(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(seconds=settings.jwt_expires_in)
    payload = {
        "sub": subject,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password
import uuid


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, username: str, password: str, email: str | None):
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

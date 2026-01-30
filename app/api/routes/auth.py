from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.response import ok, error
from app.core.security import verify_password, create_access_token
from app.crud.user import get_user_by_username, create_user
from app.schemas.auth import LoginIn, RegisterIn
from app.core.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if get_user_by_username(db, payload.username):
        return error(40901, "username_exists", status_code=409)
    user = create_user(db, payload.username, payload.password, payload.email)
    return ok({"id": user.id, "username": user.username})


@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = get_user_by_username(db, payload.username)
    if not user or not verify_password(payload.password, user.password_hash):
        return error(40101, "invalid_credentials", status_code=401)
    token = create_access_token(user.id)
    settings = get_settings()
    return ok(
        {
            "access_token": token,
            "expires_in": settings.jwt_expires_in,
            "user": {
                "id": user.id,
                "username": user.username,
                "avatar_url": user.avatar_url or "",
            },
        }
    )

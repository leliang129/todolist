from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_superadmin
from app.core.database import get_db
from app.core.response import ok, error
from app.crud.user import create_user, get_user_by_username
from app.schemas.user import UserCreate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def me(user=Depends(get_current_user)):
    return ok(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "role": user.role,
        }
    )


@router.post("")
def create(payload: UserCreate, db: Session = Depends(get_db), _=Depends(require_superadmin)):
    if get_user_by_username(db, payload.username):
        return error(40901, "username_exists", status_code=409)
    user = create_user(db, payload.username, payload.password, payload.email, payload.role)
    return ok(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "role": user.role,
        }
    )

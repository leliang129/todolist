from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.core.response import ok

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def me(user=Depends(get_current_user)):
    return ok(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar_url": user.avatar_url,
        }
    )

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.response import ok
from app.crud.todo import stats_summary

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary")
def summary(db: Session = Depends(get_db), user=Depends(get_current_user)):
    data = stats_summary(db, user.id)
    return ok(data)

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.response import ok, paginated, error
from app.crud.todo import list_trash, restore_todo, purge_todo, clear_trash
from app.models.todo import Todo

router = APIRouter(prefix="/trash", tags=["trash"])


def serialize(todo: Todo):
    return {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "priority": todo.priority,
        "status": todo.status,
        "due_date": todo.due_date,
        "remind_at": todo.remind_at,
        "category_id": todo.category_id,
        "tags": todo.tags,
        "is_deleted": todo.is_deleted,
        "deleted_at": todo.deleted_at,
        "completed_at": todo.completed_at,
        "created_at": todo.created_at,
        "updated_at": todo.updated_at,
    }


@router.get("")
def get_trash(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = list_trash(db, user.id, page, page_size)
    return paginated([serialize(item) for item in items], page, page_size, total)


@router.post("/{todo_id}/restore")
def restore(todo_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user.id, Todo.is_deleted.is_(True)).first()
    if not todo:
        return error(40401, "todo_not_found", status_code=404)
    restore_todo(db, todo)
    return ok({})


@router.delete("/{todo_id}/purge")
def purge(todo_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user.id, Todo.is_deleted.is_(True)).first()
    if not todo:
        return error(40401, "todo_not_found", status_code=404)
    purge_todo(db, todo)
    return ok({})


@router.delete("/clear")
def clear(db: Session = Depends(get_db), user=Depends(get_current_user)):
    clear_trash(db, user.id)
    return ok({})

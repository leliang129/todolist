from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.response import ok, paginated, error
from app.crud.todo import (
    list_todos,
    create_todo,
    update_todo,
    soft_delete_todo,
    batch_status,
    clear_done,
)
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate, TodoBatchStatus

router = APIRouter(prefix="/todos", tags=["todos"])


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
def get_todos(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    status: str | None = None,
    category_id: str | None = None,
    priority: str | None = None,
    keyword: str | None = None,
    due: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
    include_deleted: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    filters = {
        "status": status,
        "category_id": category_id,
        "priority": priority,
        "keyword": keyword,
        "due": due,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "include_deleted": include_deleted,
    }
    items, total = list_todos(db, user.id, filters, page, page_size)
    return paginated([serialize(item) for item in items], page, page_size, total)


@router.post("")
def create(payload: TodoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    todo = create_todo(db, user.id, payload.model_dump())
    return ok(serialize(todo))


@router.put("/{todo_id}")
def update(todo_id: str, payload: TodoUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user.id).first()
    if not todo:
        return error(40401, "todo_not_found", status_code=404)
    todo = update_todo(db, todo, payload.model_dump(exclude_unset=True))
    return ok(serialize(todo))


@router.delete("/{todo_id}")
def remove(todo_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user.id).first()
    if not todo:
        return error(40401, "todo_not_found", status_code=404)
    soft_delete_todo(db, todo)
    return ok({})


@router.patch("/batch/status")
def update_batch(payload: TodoBatchStatus, db: Session = Depends(get_db), user=Depends(get_current_user)):
    batch_status(db, user.id, payload.ids, payload.status)
    return ok({})


@router.delete("/clear-done")
def clear_done_items(db: Session = Depends(get_db), user=Depends(get_current_user)):
    clear_done(db, user.id)
    return ok({})

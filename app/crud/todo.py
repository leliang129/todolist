from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.todo import Todo
from datetime import date, datetime, timedelta, time
import uuid


PRIORITY_ORDER = {
    "high": 3,
    "medium": 2,
    "low": 1,
}


def build_filters(query, user_id: str, filters: dict):
    query = query.filter(Todo.user_id == user_id)
    include_deleted = filters.get("include_deleted")
    if not include_deleted:
        query = query.filter(Todo.is_deleted.is_(False))

    status = filters.get("status")
    if status:
        query = query.filter(Todo.status == status)

    category_id = filters.get("category_id")
    if category_id:
        query = query.filter(Todo.category_id == category_id)

    priority = filters.get("priority")
    if priority:
        query = query.filter(Todo.priority == priority)

    keyword = filters.get("keyword")
    if keyword:
        like = f"%{keyword}%"
        query = query.filter((Todo.title.ilike(like)) | (Todo.description.ilike(like)))

    due = filters.get("due")
    if due:
        today = date.today()
        if due == "today":
            query = query.filter(Todo.due_date == today)
        elif due == "week":
            week_end = today + timedelta(days=7)
            query = query.filter(Todo.due_date >= today, Todo.due_date <= week_end)
        elif due == "overdue":
            query = query.filter(Todo.due_date < today)
        elif due == "none":
            query = query.filter(Todo.due_date.is_(None))

    return query


def list_todos(db: Session, user_id: str, filters: dict, page: int, page_size: int):
    base = db.query(Todo)
    base = build_filters(base, user_id, filters)

    total = base.count()

    sort_by = filters.get("sort_by") or "created_at"
    sort_order = filters.get("sort_order") or "desc"

    if sort_by == "due_date":
        order_col = Todo.due_date
    elif sort_by == "priority":
        order_col = case(
            (Todo.priority == "high", PRIORITY_ORDER["high"]),
            (Todo.priority == "medium", PRIORITY_ORDER["medium"]),
            (Todo.priority == "low", PRIORITY_ORDER["low"]),
            else_=0,
        )
    else:
        order_col = Todo.created_at

    if sort_order == "asc":
        base = base.order_by(order_col.asc())
    else:
        base = base.order_by(order_col.desc())

    items = base.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def create_todo(db: Session, user_id: str, data: dict):
    todo = Todo(
        id=str(uuid.uuid4()),
        user_id=user_id,
        **data,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def update_todo(db: Session, todo: Todo, data: dict):
    for key, value in data.items():
        if value is not None:
            setattr(todo, key, value)
    if todo.status == "done" and todo.completed_at is None:
        todo.completed_at = datetime.utcnow()
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def soft_delete_todo(db: Session, todo: Todo):
    todo.is_deleted = True
    todo.deleted_at = datetime.utcnow()
    db.add(todo)
    db.commit()


def restore_todo(db: Session, todo: Todo):
    todo.is_deleted = False
    todo.deleted_at = None
    db.add(todo)
    db.commit()


def purge_todo(db: Session, todo: Todo):
    db.delete(todo)
    db.commit()


def clear_done(db: Session, user_id: str):
    q = db.query(Todo).filter(
        Todo.user_id == user_id,
        Todo.status == "done",
        Todo.is_deleted.is_(False),
    )
    for item in q.all():
        item.is_deleted = True
        item.deleted_at = datetime.utcnow()
        db.add(item)
    db.commit()


def batch_status(db: Session, user_id: str, ids: list[str], status: str):
    q = db.query(Todo).filter(Todo.user_id == user_id, Todo.id.in_(ids))
    for item in q.all():
        item.status = status
        if status == "done" and item.completed_at is None:
            item.completed_at = datetime.utcnow()
        db.add(item)
    db.commit()


def list_trash(db: Session, user_id: str, page: int, page_size: int):
    q = db.query(Todo).filter(Todo.user_id == user_id, Todo.is_deleted.is_(True))
    total = q.count()
    items = q.order_by(Todo.deleted_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def clear_trash(db: Session, user_id: str):
    q = db.query(Todo).filter(Todo.user_id == user_id, Todo.is_deleted.is_(True))
    for item in q.all():
        db.delete(item)
    db.commit()


def stats_summary(db: Session, user_id: str):
    total = db.query(func.count(Todo.id)).filter(Todo.user_id == user_id, Todo.is_deleted.is_(False)).scalar() or 0
    today = date.today()
    today_completed = (
        db.query(func.count(Todo.id))
        .filter(Todo.user_id == user_id, Todo.status == "done", func.date(Todo.completed_at) == today)
        .scalar()
        or 0
    )
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_start_dt = datetime.combine(week_start, time.min)
    week_end_dt = datetime.combine(week_end, time.max)
    week_done = (
        db.query(func.count(Todo.id))
        .filter(Todo.user_id == user_id, Todo.status == "done", Todo.completed_at >= week_start_dt, Todo.completed_at <= week_end_dt)
        .scalar()
        or 0
    )
    week_total = (
        db.query(func.count(Todo.id))
        .filter(Todo.user_id == user_id, Todo.created_at >= week_start_dt, Todo.created_at <= week_end_dt, Todo.is_deleted.is_(False))
        .scalar()
        or 0
    )
    rate = round(week_done / week_total, 2) if week_total else 0.0
    return {"total_todos": total, "today_completed": today_completed, "week_completion_rate": rate}

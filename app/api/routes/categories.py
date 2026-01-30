from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.response import ok, error
from app.crud.category import list_categories, create_category, update_category, delete_category
from app.models.category import Category
from app.models.todo import Todo
from app.schemas.category import CategoryCreate, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("")
def get_categories(db: Session = Depends(get_db), user=Depends(get_current_user)):
    items = list_categories(db, user.id)
    return ok([{
        "id": item.id,
        "name": item.name,
        "color": item.color,
        "order": item.order,
        "is_system": item.is_system,
    } for item in items])


@router.post("")
def create(payload: CategoryCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    existing = db.query(Category).filter(Category.user_id == user.id, Category.name == payload.name).first()
    if existing:
        return error(40901, "category_exists", status_code=409)
    item = create_category(db, user.id, payload.name, payload.color, payload.order or 0)
    return ok({
        "id": item.id,
        "name": item.name,
        "color": item.color,
        "order": item.order,
        "is_system": item.is_system,
    })


@router.put("/{category_id}")
def update(category_id: str, payload: CategoryUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    category = db.query(Category).filter(Category.id == category_id, Category.user_id == user.id).first()
    if not category:
        return error(40401, "category_not_found", status_code=404)
    data = payload.model_dump(exclude_unset=True)
    item = update_category(db, category, data)
    return ok({
        "id": item.id,
        "name": item.name,
        "color": item.color,
        "order": item.order,
        "is_system": item.is_system,
    })


@router.delete("/{category_id}")
def remove(category_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    category = db.query(Category).filter(Category.id == category_id, Category.user_id == user.id).first()
    if not category:
        return error(40401, "category_not_found", status_code=404)
    db.query(Todo).filter(Todo.user_id == user.id, Todo.category_id == category_id).update({"category_id": None})
    delete_category(db, category)
    return ok({})

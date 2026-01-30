from sqlalchemy.orm import Session
from app.models.category import Category
import uuid


def list_categories(db: Session, user_id: str):
    return (
        db.query(Category)
        .filter(Category.user_id == user_id)
        .order_by(Category.order.asc())
        .all()
    )


def create_category(db: Session, user_id: str, name: str, color: str, order: int):
    category = Category(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name=name,
        color=color,
        order=order or 0,
        is_system=False,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category: Category, data: dict):
    for key, value in data.items():
        if value is not None:
            setattr(category, key, value)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: Category):
    db.delete(category)
    db.commit()

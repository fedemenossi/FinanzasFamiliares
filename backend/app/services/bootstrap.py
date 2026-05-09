from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category
from app.services.classifier import SYSTEM_CATEGORIES


def ensure_user_categories(db: Session, user_id: int) -> None:
    existing = set(
        db.scalars(select(Category.name).where(Category.user_id == user_id)).all()
    )
    for name, color in SYSTEM_CATEGORIES:
        if name not in existing:
            db.add(Category(user_id=user_id, name=name, color=color, is_system=True))
    db.commit()


def get_category_by_name(db: Session, user_id: int, name: str) -> Category:
    category = db.scalar(select(Category).where(Category.user_id == user_id, Category.name == name))
    if not category:
        category = Category(user_id=user_id, name=name, is_system=False)
        db.add(category)
        db.flush()
    return category

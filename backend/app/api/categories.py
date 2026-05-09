from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Category, User
from app.schemas import CategoryOut
from app.services.bootstrap import ensure_user_categories

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_user_categories(db, current_user.id)
    return db.scalars(select(Category).where(Category.user_id == current_user.id).order_by(Category.name)).all()

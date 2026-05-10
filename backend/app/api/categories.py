from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Category, User
from app.schemas import CategoryCreate, CategoryOut, CategoryUpdate
from app.services.bootstrap import ensure_user_categories

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_user_categories(db, current_user.id)
    return db.scalars(select(Category).where(Category.user_id == current_user.id, Category.is_active == True).order_by(Category.name)).all()


@router.post("", response_model=CategoryOut)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="El nombre es obligatorio")
    existing = db.scalar(select(Category).where(Category.user_id == current_user.id, Category.name == name))
    if existing:
        if not existing.is_active:
            existing.is_active = True
            existing.color = payload.color
            db.commit()
            db.refresh(existing)
            return existing
        raise HTTPException(status_code=409, detail="La categoria ya existe")
    category = Category(user_id=current_user.id, name=name, color=payload.color, is_system=False, is_active=True)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = db.scalar(select(Category).where(Category.id == category_id, Category.user_id == current_user.id))
    if not category:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="El nombre es obligatorio")
        duplicate = db.scalar(select(Category).where(Category.user_id == current_user.id, Category.name == name, Category.id != category_id))
        if duplicate:
            raise HTTPException(status_code=409, detail="Ya existe una categoria con ese nombre")
        category.name = name
    if payload.color is not None:
        category.color = payload.color
    if payload.is_active is not None:
        category.is_active = payload.is_active
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = db.scalar(select(Category).where(Category.id == category_id, Category.user_id == current_user.id))
    if not category:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    category.is_active = False
    db.commit()
    return {"status": "deleted"}

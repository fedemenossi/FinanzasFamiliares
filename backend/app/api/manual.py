from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import IncomeCategory, ManualExpense, ManualIncome, User
from app.schemas import (
    IncomeCategoryCreate,
    IncomeCategoryOut,
    IncomeCategoryUpdate,
    ManualExpenseCreate,
    ManualExpenseOut,
    ManualIncomeCreate,
    ManualIncomeOut,
)

router = APIRouter(prefix="/manual", tags=["manual"])


@router.post("/expenses", response_model=ManualExpenseOut)
def create_expense(payload: ManualExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expense = ManualExpense(user_id=current_user.id, **payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/expenses", response_model=list[ManualExpenseOut])
def list_expenses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.scalars(select(ManualExpense).where(ManualExpense.user_id == current_user.id).order_by(ManualExpense.expense_date.desc())).all()


@router.post("/income", response_model=ManualIncomeOut)
def create_income(payload: ManualIncomeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = db.get(IncomeCategory, payload.income_category_id)
    if not category or not category.is_active:
        raise HTTPException(status_code=400, detail="Categoria de ingreso invalida")
    income = ManualIncome(user_id=current_user.id, **payload.model_dump())
    db.add(income)
    db.commit()
    db.refresh(income)
    income = db.scalar(select(ManualIncome).options(joinedload(ManualIncome.income_category)).where(ManualIncome.id == income.id))
    return income


@router.get("/income", response_model=list[ManualIncomeOut])
def list_income(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.scalars(
        select(ManualIncome)
        .options(joinedload(ManualIncome.income_category))
        .where(ManualIncome.user_id == current_user.id)
        .order_by(ManualIncome.income_date.desc())
    ).all()


@router.get("/income-categories", response_model=list[IncomeCategoryOut])
def list_income_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.scalars(select(IncomeCategory).where(IncomeCategory.is_active == True).order_by(IncomeCategory.id)).all()


@router.post("/income-categories", response_model=IncomeCategoryOut)
def create_income_category(payload: IncomeCategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="El nombre es obligatorio")
    existing = db.scalar(select(IncomeCategory).where(IncomeCategory.name == name))
    if existing:
        if not existing.is_active:
            existing.is_active = True
            existing.color = payload.color
            db.commit()
            db.refresh(existing)
            return existing
        raise HTTPException(status_code=409, detail="La categoria de ingreso ya existe")
    category = IncomeCategory(name=name, color=payload.color, is_system=False, is_active=True)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.patch("/income-categories/{category_id}", response_model=IncomeCategoryOut)
def update_income_category(
    category_id: int,
    payload: IncomeCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = db.get(IncomeCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria de ingreso no encontrada")
    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="El nombre es obligatorio")
        duplicate = db.scalar(select(IncomeCategory).where(IncomeCategory.name == name, IncomeCategory.id != category_id))
        if duplicate:
            raise HTTPException(status_code=409, detail="Ya existe una categoria de ingreso con ese nombre")
        category.name = name
    if payload.color is not None:
        category.color = payload.color
    if payload.is_active is not None:
        category.is_active = payload.is_active
    db.commit()
    db.refresh(category)
    return category


@router.delete("/income-categories/{category_id}")
def delete_income_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = db.get(IncomeCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria de ingreso no encontrada")
    category.is_active = False
    db.commit()
    return {"status": "deleted"}

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import ManualExpense, ManualIncome, User
from app.schemas import ManualExpenseCreate, ManualExpenseOut, ManualIncomeCreate, ManualIncomeOut

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
    income = ManualIncome(user_id=current_user.id, **payload.model_dump())
    db.add(income)
    db.commit()
    db.refresh(income)
    return income


@router.get("/income", response_model=list[ManualIncomeOut])
def list_income(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.scalars(select(ManualIncome).where(ManualIncome.user_id == current_user.id).order_by(ManualIncome.income_date.desc())).all()

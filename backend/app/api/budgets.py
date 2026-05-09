from calendar import monthrange
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Budget, ManualExpense, Transaction, User
from app.schemas import BudgetCreate, BudgetOut

router = APIRouter(prefix="/budgets", tags=["budgets"])


def month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="El mes debe estar entre 1 y 12")
    start = datetime(year, month, 1)
    end = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)
    return start, end


def category_spending(db: Session, user_id: int, category_id: int, year: int, month: int) -> Decimal:
    start, end = month_bounds(year, month)
    transactions = db.scalars(
        select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.category_id == category_id,
            Transaction.transaction_date >= start,
            Transaction.transaction_date <= end,
        )
    ).all()
    manual_expenses = db.scalars(
        select(ManualExpense).where(
            ManualExpense.user_id == user_id,
            ManualExpense.category_id == category_id,
            ManualExpense.expense_date >= start,
            ManualExpense.expense_date <= end,
        )
    ).all()
    return sum((abs(t.amount) for t in transactions), Decimal("0")) + sum((e.amount for e in manual_expenses), Decimal("0"))


def enrich_budget(db: Session, budget: Budget) -> BudgetOut:
    spent = category_spending(db, budget.user_id, budget.category_id, budget.year, budget.month)
    remaining = budget.amount - spent
    usage = float((spent / budget.amount * 100) if budget.amount else 0)
    return BudgetOut(
        id=budget.id,
        category_id=budget.category_id,
        year=budget.year,
        month=budget.month,
        amount=budget.amount,
        notes=budget.notes,
        category=budget.category,
        spent=spent,
        remaining=remaining,
        usage_percent=usage,
    )


@router.get("", response_model=list[BudgetOut])
def list_budgets(
    year: int | None = Query(default=None),
    month: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    year = year or now.year
    month = month or now.month
    month_bounds(year, month)
    budgets = db.scalars(
        select(Budget)
        .options(joinedload(Budget.category))
        .where(Budget.user_id == current_user.id, Budget.year == year, Budget.month == month)
        .order_by(Budget.id.desc())
    ).all()
    return [enrich_budget(db, budget) for budget in budgets]


@router.post("", response_model=BudgetOut)
def upsert_budget(payload: BudgetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    month_bounds(payload.year, payload.month)
    budget = db.scalar(
        select(Budget)
        .options(joinedload(Budget.category))
        .where(
            Budget.user_id == current_user.id,
            Budget.category_id == payload.category_id,
            Budget.year == payload.year,
            Budget.month == payload.month,
        )
    )
    if budget:
        budget.amount = payload.amount
        budget.notes = payload.notes
    else:
        budget = Budget(user_id=current_user.id, **payload.model_dump())
        db.add(budget)
    db.commit()
    db.refresh(budget)
    budget = db.scalar(select(Budget).options(joinedload(Budget.category)).where(Budget.id == budget.id))
    return enrich_budget(db, budget)


@router.delete("/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    budget = db.scalar(select(Budget).where(Budget.id == budget_id, Budget.user_id == current_user.id))
    if not budget:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    db.delete(budget)
    db.commit()
    return {"status": "deleted"}

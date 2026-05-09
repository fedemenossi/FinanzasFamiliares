from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import ManualExpense, ManualIncome, Transaction, User
from app.schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.scalars(
        select(Transaction)
        .options(joinedload(Transaction.category))
        .where(Transaction.user_id == current_user.id)
    ).all()
    manual_expenses = db.scalars(select(ManualExpense).where(ManualExpense.user_id == current_user.id)).all()
    incomes = db.scalars(select(ManualIncome).where(ManualIncome.user_id == current_user.id)).all()

    income_total = sum((i.amount for i in incomes), Decimal("0"))
    tx_expenses = sum((abs(t.amount) for t in transactions if t.amount > 0), Decimal("0"))
    manual_total = sum((e.amount for e in manual_expenses), Decimal("0"))
    expense_total = tx_expenses + manual_total
    savings = income_total - expense_total
    savings_rate = float((savings / income_total * 100) if income_total else 0)

    by_category: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    monthly: defaultdict[str, dict[str, Decimal]] = defaultdict(lambda: {"income": Decimal("0"), "expenses": Decimal("0")})
    fixed_variable: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    merchant_counter: Counter[str] = Counter()

    for transaction in transactions:
        amount = abs(transaction.amount)
        category = transaction.category.name if transaction.category else "Otros"
        by_category[category] += amount
        monthly[transaction.transaction_date.strftime("%Y-%m")]["expenses"] += amount
        fixed_variable[transaction.expense_type] += amount
        merchant_counter[transaction.normalized_description] += 1

    for expense in manual_expenses:
        amount = abs(expense.amount)
        by_category["Manual"] += amount
        monthly[expense.expense_date.strftime("%Y-%m")]["expenses"] += amount
        fixed_variable[expense.expense_type] += amount

    for income in incomes:
        monthly[income.income_date.strftime("%Y-%m")]["income"] += income.amount

    top_expenses = sorted(
        [
            {"date": t.transaction_date.isoformat(), "description": t.normalized_description, "amount": float(abs(t.amount))}
            for t in transactions
        ],
        key=lambda item: item["amount"],
        reverse=True,
    )[:10]

    small_expenses = [
        {"description": desc, "count": count}
        for desc, count in merchant_counter.most_common()
        if count >= 2
    ][:10]

    return DashboardSummary(
        income=income_total,
        expenses=expense_total,
        savings=savings,
        savings_rate=savings_rate,
        expenses_by_category=[{"category": k, "amount": float(v)} for k, v in sorted(by_category.items(), key=lambda x: x[1], reverse=True)],
        monthly_evolution=[{"month": k, "income": float(v["income"]), "expenses": float(v["expenses"])} for k, v in sorted(monthly.items())],
        fixed_vs_variable=[{"type": k, "amount": float(v)} for k, v in fixed_variable.items()],
        top_expenses=top_expenses,
        frequent_merchants=[{"merchant": k, "count": v} for k, v in merchant_counter.most_common(10)],
        small_expenses=small_expenses,
    )

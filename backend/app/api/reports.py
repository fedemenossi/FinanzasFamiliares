from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Category, IncomeCategory, ManualExpense, ManualIncome, Transaction, User
from app.schemas import (
    FinancialQueryBreakdown,
    FinancialQueryGroup,
    FinancialQueryResult,
    FinancialQueryRow,
    FinancialQuerySummary,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/cashflow", response_model=FinancialQueryResult)
def cashflow_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_by: Literal["month", "year"] = Query(default="month"),
    record_type: Literal["all", "income", "expense"] = Query(default="all"),
    source: Literal["all", "pdf", "manual"] = Query(default="all"),
    expense_category_id: int | None = Query(default=None),
    income_category_id: int | None = Query(default=None),
    flow_type: str | None = Query(default=None),
    year: int | None = Query(default=None, ge=2000, le=2100),
    month: int | None = Query(default=None, ge=1, le=12),
    exact_date: date | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    q: str | None = Query(default=None),
    limit: int = Query(default=500, ge=1, le=2000),
):
    rows: list[FinancialQueryRow] = []
    q_normalized = q.upper().strip() if q else None

    category_names = {
        category.id: category.name
        for category in db.scalars(select(Category).where(Category.user_id == current_user.id)).all()
    }
    income_category_names = {
        category.id: category.name
        for category in db.scalars(select(IncomeCategory)).all()
    }

    if record_type in ("all", "expense") and source in ("all", "pdf"):
        transactions = db.scalars(
            select(Transaction)
            .options(joinedload(Transaction.category))
            .where(Transaction.user_id == current_user.id, Transaction.amount > 0)
        ).all()
        for transaction in transactions:
            category_name = transaction.category.name if transaction.category else "Sin categoria"
            row = FinancialQueryRow(
                id=transaction.id,
                kind="expense",
                source="pdf",
                date=transaction.transaction_date,
                period=format_period(transaction.transaction_date, group_by),
                description=transaction.normalized_description,
                category_id=transaction.category_id,
                category=category_name,
                flow_type=transaction.expense_type,
                amount=abs(transaction.amount),
                signed_amount=-abs(transaction.amount),
                bank_name=transaction.bank_name,
                card_type=transaction.card_type or transaction.card_brand,
            )
            if row_matches(row, q_normalized, year, month, exact_date, date_from, date_to, flow_type):
                rows.append(row)

    if record_type in ("all", "expense") and source in ("all", "manual"):
        manual_expenses = db.scalars(
            select(ManualExpense).where(ManualExpense.user_id == current_user.id)
        ).all()
        for expense in manual_expenses:
            category_name = category_names.get(expense.category_id or 0, "Sin categoria")
            row = FinancialQueryRow(
                id=expense.id,
                kind="expense",
                source="manual",
                date=expense.expense_date,
                period=format_period(expense.expense_date, group_by),
                description=expense.description,
                category_id=expense.category_id,
                category=category_name,
                flow_type=expense.expense_type,
                amount=abs(expense.amount),
                signed_amount=-abs(expense.amount),
            )
            if row_matches(row, q_normalized, year, month, exact_date, date_from, date_to, flow_type):
                rows.append(row)

    if record_type in ("all", "income") and source in ("all", "manual"):
        incomes = db.scalars(
            select(ManualIncome)
            .options(joinedload(ManualIncome.income_category))
            .where(ManualIncome.user_id == current_user.id)
        ).all()
        for income in incomes:
            category_name = income.income_category.name if income.income_category else income_category_names.get(income.income_category_id, "Sin categoria")
            row = FinancialQueryRow(
                id=income.id,
                kind="income",
                source="manual",
                date=income.income_date,
                period=format_period(income.income_date, group_by),
                description=income.description,
                category_id=income.income_category_id,
                category=category_name,
                flow_type=income.income_type,
                amount=income.amount,
                signed_amount=income.amount,
            )
            if row_matches(row, q_normalized, year, month, exact_date, date_from, date_to, flow_type):
                rows.append(row)

    rows = [
        row
        for row in rows
        if category_matches(row, expense_category_id, income_category_id)
    ]
    rows.sort(key=lambda row: (row.date, row.kind, row.id), reverse=True)
    limited_rows = rows[:limit]

    income_total = sum((row.amount for row in rows if row.kind == "income"), Decimal("0"))
    expense_total = sum((row.amount for row in rows if row.kind == "expense"), Decimal("0"))
    savings = income_total - expense_total
    savings_rate = float((savings / income_total * 100) if income_total else 0)

    return FinancialQueryResult(
        summary=FinancialQuerySummary(
            income=income_total,
            expenses=expense_total,
            savings=savings,
            savings_rate=savings_rate,
            row_count=len(rows),
        ),
        group_by=group_by,
        groups=build_groups(rows),
        by_category=build_breakdown(rows, "category"),
        by_type=build_breakdown(rows, "flow_type"),
        rows=limited_rows,
    )


def row_matches(
    row: FinancialQueryRow,
    q: str | None,
    year: int | None,
    month: int | None,
    exact_date: date | None,
    date_from: date | None,
    date_to: date | None,
    flow_type: str | None,
) -> bool:
    row_date = row.date.date()
    if year and row.date.year != year:
        return False
    if month and row.date.month != month:
        return False
    if exact_date and row_date != exact_date:
        return False
    if date_from and row_date < date_from:
        return False
    if date_to and row_date > date_to:
        return False
    if flow_type and row.flow_type != flow_type:
        return False
    if q and q not in row.description.upper() and q not in row.category.upper():
        return False
    return True


def category_matches(row: FinancialQueryRow, expense_category_id: int | None, income_category_id: int | None) -> bool:
    if row.kind == "expense" and expense_category_id and row.category_id != expense_category_id:
        return False
    if row.kind == "income" and income_category_id and row.category_id != income_category_id:
        return False
    if row.kind == "income" and expense_category_id and not income_category_id:
        return False
    if row.kind == "expense" and income_category_id and not expense_category_id:
        return False
    return True


def format_period(value: datetime, group_by: Literal["month", "year"]) -> str:
    if group_by == "year":
        return str(value.year)
    return value.strftime("%Y-%m")


def build_groups(rows: list[FinancialQueryRow]) -> list[FinancialQueryGroup]:
    grouped: dict[str, dict[str, Decimal | int]] = defaultdict(
        lambda: {"income": Decimal("0"), "expenses": Decimal("0"), "count": 0}
    )
    for row in rows:
        bucket = grouped[row.period]
        if row.kind == "income":
            bucket["income"] += row.amount
        else:
            bucket["expenses"] += row.amount
        bucket["count"] += 1

    result: list[FinancialQueryGroup] = []
    for key in sorted(grouped):
        income = grouped[key]["income"]
        expenses = grouped[key]["expenses"]
        result.append(
            FinancialQueryGroup(
                key=key,
                label=key,
                income=income,
                expenses=expenses,
                savings=income - expenses,
                count=grouped[key]["count"],
            )
        )
    return result


def build_breakdown(rows: list[FinancialQueryRow], field: Literal["category", "flow_type"]) -> list[FinancialQueryBreakdown]:
    grouped: dict[tuple[str, str], dict[str, Decimal | int]] = defaultdict(lambda: {"amount": Decimal("0"), "count": 0})
    for row in rows:
        label = row.category if field == "category" else row.flow_type
        key = (row.kind, label or "Sin dato")
        grouped[key]["amount"] += row.amount
        grouped[key]["count"] += 1

    items = [
        FinancialQueryBreakdown(
            key=f"{kind}:{label}",
            label=label,
            kind=kind,
            amount=data["amount"],
            count=data["count"],
        )
        for (kind, label), data in grouped.items()
    ]
    return sorted(items, key=lambda item: item.amount, reverse=True)

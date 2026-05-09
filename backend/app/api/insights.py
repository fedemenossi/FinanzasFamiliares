from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.budgets import category_spending
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Budget, ManualIncome, Transaction, User
from app.schemas import InsightOut

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("", response_model=list[InsightOut])
def list_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    now = datetime.utcnow()
    insights: list[InsightOut] = []
    transactions = db.scalars(
        select(Transaction)
        .options(joinedload(Transaction.category))
        .where(Transaction.user_id == current_user.id)
    ).all()
    incomes = db.scalars(select(ManualIncome).where(ManualIncome.user_id == current_user.id)).all()
    budgets = db.scalars(
        select(Budget)
        .options(joinedload(Budget.category))
        .where(Budget.user_id == current_user.id, Budget.year == now.year, Budget.month == now.month)
    ).all()

    income_total = sum((i.amount for i in incomes if i.income_date.year == now.year and i.income_date.month == now.month), Decimal("0"))
    current_month_expenses = sum(
        (
            abs(t.amount)
            for t in transactions
            if t.transaction_date.year == now.year and t.transaction_date.month == now.month
        ),
        Decimal("0"),
    )
    if income_total:
        savings_rate = float((income_total - current_month_expenses) / income_total * 100)
        if savings_rate < 10:
            insights.append(
                InsightOut(
                    level="warning",
                    title="Ahorro mensual bajo",
                    detail=f"El ahorro estimado del mes es {savings_rate:.1f}%. Revisá gastos variables y suscripciones.",
                    metric=savings_rate,
                )
            )
        elif savings_rate >= 20:
            insights.append(
                InsightOut(
                    level="success",
                    title="Buen nivel de ahorro",
                    detail=f"El ahorro estimado del mes es {savings_rate:.1f}%. Hay margen para inversión o fondo de emergencia.",
                    metric=savings_rate,
                )
            )

    fixed_total = sum(
        (
            abs(t.amount)
            for t in transactions
            if t.expense_type == "fixed" and t.transaction_date.year == now.year and t.transaction_date.month == now.month
        ),
        Decimal("0"),
    )
    if income_total:
        fixed_ratio = float(fixed_total / income_total * 100)
        if fixed_ratio > 55:
            insights.append(
                InsightOut(
                    level="danger",
                    title="Carga fija alta",
                    detail=f"Los gastos fijos representan {fixed_ratio:.1f}% de los ingresos del mes.",
                    metric=fixed_ratio,
                )
            )

    for budget in budgets:
        spent = category_spending(db, current_user.id, budget.category_id, budget.year, budget.month)
        usage = float((spent / budget.amount * 100) if budget.amount else 0)
        if usage >= 100:
            insights.append(
                InsightOut(
                    level="danger",
                    title=f"Presupuesto excedido: {budget.category.name}",
                    detail=f"Se gastó {usage:.1f}% del presupuesto mensual de la categoría.",
                    metric=usage,
                )
            )
        elif usage >= 80:
            insights.append(
                InsightOut(
                    level="warning",
                    title=f"Presupuesto casi agotado: {budget.category.name}",
                    detail=f"Ya se usó {usage:.1f}% del presupuesto mensual.",
                    metric=usage,
                )
            )

    merchant_counter: Counter[str] = Counter()
    merchant_amounts: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for transaction in transactions:
        if transaction.transaction_date.year == now.year and transaction.transaction_date.month == now.month:
            merchant_counter[transaction.normalized_description] += 1
            merchant_amounts[transaction.normalized_description] += abs(transaction.amount)

    for merchant, count in merchant_counter.most_common(5):
        if count >= 4 and merchant_amounts[merchant] <= Decimal("50000"):
            insights.append(
                InsightOut(
                    level="info",
                    title="Gasto hormiga detectado",
                    detail=f"{merchant} aparece {count} veces este mes por un total de ${merchant_amounts[merchant]:,.2f}.",
                    metric=float(merchant_amounts[merchant]),
                )
            )

    if not insights:
        insights.append(
            InsightOut(
                level="info",
                title="Sin alertas críticas",
                detail="Con los datos cargados no se detectan desvíos importantes este mes.",
            )
        )
    return insights

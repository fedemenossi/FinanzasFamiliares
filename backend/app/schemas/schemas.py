from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CategoryOut(BaseModel):
    id: int
    name: str
    color: str | None = None

    model_config = {"from_attributes": True}


class TransactionOut(BaseModel):
    id: int
    transaction_date: datetime
    raw_description: str
    normalized_description: str
    amount: Decimal
    currency: str
    bank_name: str | None = None
    card_brand: str | None = None
    card_type: str | None = None
    card_last_digits: str | None = None
    is_installment: bool
    installment_current: int | None = None
    installment_total: int | None = None
    expense_type: str
    category: CategoryOut | None = None

    model_config = {"from_attributes": True}


class TransactionUpdate(BaseModel):
    category_id: int | None = None
    normalized_description: str | None = None
    expense_type: str | None = None


class ManualExpenseCreate(BaseModel):
    expense_date: datetime
    category_id: int | None = None
    description: str
    amount: Decimal
    notes: str | None = None
    expense_type: str = "variable"


class ManualIncomeCreate(BaseModel):
    income_date: datetime
    description: str
    amount: Decimal
    notes: str | None = None


class ManualExpenseOut(ManualExpenseCreate):
    id: int
    model_config = {"from_attributes": True}


class ManualIncomeOut(ManualIncomeCreate):
    id: int
    model_config = {"from_attributes": True}


class DashboardSummary(BaseModel):
    income: Decimal
    expenses: Decimal
    savings: Decimal
    savings_rate: float
    expenses_by_category: list[dict]
    monthly_evolution: list[dict]
    fixed_vs_variable: list[dict]
    top_expenses: list[dict]
    frequent_merchants: list[dict]
    small_expenses: list[dict]


class BudgetCreate(BaseModel):
    category_id: int
    year: int
    month: int
    amount: Decimal
    notes: str | None = None


class BudgetOut(BudgetCreate):
    id: int
    category: CategoryOut | None = None
    spent: Decimal = Decimal("0")
    remaining: Decimal = Decimal("0")
    usage_percent: float = 0

    model_config = {"from_attributes": True}


class InsightOut(BaseModel):
    level: str
    title: str
    detail: str
    metric: float | None = None

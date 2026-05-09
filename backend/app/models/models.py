from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    DECIMAL,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Account(Base, TimestampMixin):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    bank_name: Mapped[str] = mapped_column(String(120), nullable=False)
    account_type: Mapped[str | None] = mapped_column(String(80))
    alias: Mapped[str | None] = mapped_column(String(120))


class Card(Base, TimestampMixin):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    bank_name: Mapped[str] = mapped_column(String(120), nullable=False)
    brand: Mapped[str] = mapped_column(String(40), nullable=False)
    card_type: Mapped[str | None] = mapped_column(String(80))
    last_digits: Mapped[str | None] = mapped_column(String(8))
    holder_name: Mapped[str | None] = mapped_column(String(160))


class Category(Base, TimestampMixin):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_categories_user_name"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    color: Mapped[str | None] = mapped_column(String(20))
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class UploadedFile(Base, TimestampMixin):
    __tablename__ = "uploaded_files"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_path: Mapped[str] = mapped_column(String(500), nullable=False)
    bank_name: Mapped[str | None] = mapped_column(String(120))
    statement_type: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(40), default="uploaded", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)


class StatementSummary(Base, TimestampMixin):
    __tablename__ = "statement_summaries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    uploaded_file_id: Mapped[int] = mapped_column(ForeignKey("uploaded_files.id"), index=True, nullable=False)
    bank_name: Mapped[str | None] = mapped_column(String(120))
    card_brand: Mapped[str | None] = mapped_column(String(40))
    card_type: Mapped[str | None] = mapped_column(String(80))
    statement_date: Mapped[datetime | None] = mapped_column(DateTime)
    previous_balance: Mapped[Decimal | None] = mapped_column(DECIMAL(14, 2))
    current_balance: Mapped[Decimal | None] = mapped_column(DECIMAL(14, 2))
    minimum_payment: Mapped[Decimal | None] = mapped_column(DECIMAL(14, 2))


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        Index("ix_transactions_user_date", "user_id", "transaction_date"),
        Index("ix_transactions_user_category", "user_id", "category_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    uploaded_file_id: Mapped[int | None] = mapped_column(ForeignKey("uploaded_files.id"), index=True)
    bank_name: Mapped[str | None] = mapped_column(String(120))
    card_brand: Mapped[str | None] = mapped_column(String(40))
    card_type: Mapped[str | None] = mapped_column(String(80))
    card_last_digits: Mapped[str | None] = mapped_column(String(8))
    cardholder_name: Mapped[str | None] = mapped_column(String(160))
    transaction_date: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    voucher_number: Mapped[str | None] = mapped_column(String(40))
    raw_description: Mapped[str] = mapped_column(String(500), nullable=False)
    normalized_description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="ARS", nullable=False)
    is_installment: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    installment_current: Mapped[int | None] = mapped_column(Integer)
    installment_total: Mapped[int | None] = mapped_column(Integer)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), index=True)
    expense_type: Mapped[str] = mapped_column(String(20), default="variable", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    category: Mapped[Category | None] = relationship()


class ManualExpense(Base, TimestampMixin):
    __tablename__ = "manual_expenses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    expense_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(14, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    expense_type: Mapped[str] = mapped_column(String(20), default="variable", nullable=False)


class ManualIncome(Base, TimestampMixin):
    __tablename__ = "manual_income"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    income_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(14, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class ClassificationRule(Base, TimestampMixin):
    __tablename__ = "classification_rules"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    pattern: Mapped[str] = mapped_column(String(160), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True, nullable=False)
    expense_type: Mapped[str] = mapped_column(String(20), default="variable", nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

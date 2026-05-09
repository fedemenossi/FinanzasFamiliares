"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-08
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "accounts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("bank_name", sa.String(length=120), nullable=False),
        sa.Column("account_type", sa.String(length=80), nullable=True),
        sa.Column("alias", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_accounts_user_id"), "accounts", ["user_id"])

    op.create_table(
        "cards",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("bank_name", sa.String(length=120), nullable=False),
        sa.Column("brand", sa.String(length=40), nullable=False),
        sa.Column("card_type", sa.String(length=80), nullable=True),
        sa.Column("last_digits", sa.String(length=8), nullable=True),
        sa.Column("holder_name", sa.String(length=160), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cards_user_id"), "cards", ["user_id"])

    op.create_table(
        "categories",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_categories_user_name"),
    )
    op.create_index(op.f("ix_categories_user_id"), "categories", ["user_id"])

    op.create_table(
        "uploaded_files",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_path", sa.String(length=500), nullable=False),
        sa.Column("bank_name", sa.String(length=120), nullable=True),
        sa.Column("statement_type", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_uploaded_files_user_id"), "uploaded_files", ["user_id"])

    op.create_table(
        "manual_income",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("income_date", sa.DateTime(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.DECIMAL(precision=14, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_manual_income_user_id"), "manual_income", ["user_id"])

    op.create_table(
        "manual_expenses",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("expense_date", sa.DateTime(), nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.DECIMAL(precision=14, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("expense_type", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_manual_expenses_category_id"), "manual_expenses", ["category_id"])
    op.create_index(op.f("ix_manual_expenses_user_id"), "manual_expenses", ["user_id"])

    op.create_table(
        "statement_summaries",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("uploaded_file_id", sa.BigInteger(), nullable=False),
        sa.Column("bank_name", sa.String(length=120), nullable=True),
        sa.Column("card_brand", sa.String(length=40), nullable=True),
        sa.Column("card_type", sa.String(length=80), nullable=True),
        sa.Column("statement_date", sa.DateTime(), nullable=True),
        sa.Column("previous_balance", sa.DECIMAL(precision=14, scale=2), nullable=True),
        sa.Column("current_balance", sa.DECIMAL(precision=14, scale=2), nullable=True),
        sa.Column("minimum_payment", sa.DECIMAL(precision=14, scale=2), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["uploaded_file_id"], ["uploaded_files.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_statement_summaries_uploaded_file_id"), "statement_summaries", ["uploaded_file_id"])
    op.create_index(op.f("ix_statement_summaries_user_id"), "statement_summaries", ["user_id"])

    op.create_table(
        "classification_rules",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("pattern", sa.String(length=160), nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=False),
        sa.Column("expense_type", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_classification_rules_category_id"), "classification_rules", ["category_id"])
    op.create_index(op.f("ix_classification_rules_user_id"), "classification_rules", ["user_id"])

    op.create_table(
        "transactions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("uploaded_file_id", sa.BigInteger(), nullable=True),
        sa.Column("bank_name", sa.String(length=120), nullable=True),
        sa.Column("card_brand", sa.String(length=40), nullable=True),
        sa.Column("card_type", sa.String(length=80), nullable=True),
        sa.Column("card_last_digits", sa.String(length=8), nullable=True),
        sa.Column("cardholder_name", sa.String(length=160), nullable=True),
        sa.Column("transaction_date", sa.DateTime(), nullable=False),
        sa.Column("voucher_number", sa.String(length=40), nullable=True),
        sa.Column("raw_description", sa.String(length=500), nullable=False),
        sa.Column("normalized_description", sa.String(length=500), nullable=False),
        sa.Column("amount", sa.DECIMAL(precision=14, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("is_installment", sa.Boolean(), nullable=False),
        sa.Column("installment_current", sa.Integer(), nullable=True),
        sa.Column("installment_total", sa.Integer(), nullable=True),
        sa.Column("category_id", sa.BigInteger(), nullable=True),
        sa.Column("expense_type", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["uploaded_file_id"], ["uploaded_files.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transactions_category_id"), "transactions", ["category_id"])
    op.create_index(op.f("ix_transactions_transaction_date"), "transactions", ["transaction_date"])
    op.create_index(op.f("ix_transactions_uploaded_file_id"), "transactions", ["uploaded_file_id"])
    op.create_index(op.f("ix_transactions_user_id"), "transactions", ["user_id"])
    op.create_index("ix_transactions_user_category", "transactions", ["user_id", "category_id"])
    op.create_index("ix_transactions_user_date", "transactions", ["user_id", "transaction_date"])


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("classification_rules")
    op.drop_table("statement_summaries")
    op.drop_table("manual_expenses")
    op.drop_table("manual_income")
    op.drop_table("uploaded_files")
    op.drop_table("categories")
    op.drop_table("cards")
    op.drop_table("accounts")
    op.drop_table("users")

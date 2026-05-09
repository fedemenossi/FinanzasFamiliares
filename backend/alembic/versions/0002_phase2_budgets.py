"""phase 2 budgets

Revision ID: 0002_phase2_budgets
Revises: 0001_initial_schema
Create Date: 2026-05-09
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_phase2_budgets"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "budgets",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("amount", sa.DECIMAL(precision=14, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "category_id", "year", "month", name="uq_budgets_user_category_month"),
    )
    op.create_index(op.f("ix_budgets_category_id"), "budgets", ["category_id"])
    op.create_index(op.f("ix_budgets_user_id"), "budgets", ["user_id"])
    op.create_index("ix_budgets_user_period", "budgets", ["user_id", "year", "month"])


def downgrade() -> None:
    op.drop_index("ix_budgets_user_period", table_name="budgets")
    op.drop_index(op.f("ix_budgets_user_id"), table_name="budgets")
    op.drop_index(op.f("ix_budgets_category_id"), table_name="budgets")
    op.drop_table("budgets")

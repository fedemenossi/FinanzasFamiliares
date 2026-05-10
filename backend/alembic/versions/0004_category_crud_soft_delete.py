"""category crud soft delete

Revision ID: 0004_category_crud_soft_delete
Revises: 0003_income_categories_and_types
Create Date: 2026-05-10
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_category_crud_soft_delete"
down_revision = "0003_income_categories_and_types"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("categories", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")))
    op.add_column("income_categories", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")))


def downgrade() -> None:
    op.drop_column("income_categories", "is_active")
    op.drop_column("categories", "is_active")

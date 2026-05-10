"""income categories and types

Revision ID: 0003_income_categories_and_types
Revises: 0002_phase2_budgets
Create Date: 2026-05-10
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_income_categories_and_types"
down_revision = "0002_phase2_budgets"
branch_labels = None
depends_on = None


INCOME_CATEGORIES = [
    ("Ingresos Lau", "#0f766e"),
    ("Sueldo Fede", "#2563eb"),
    ("Fondo Fede", "#7c3aed"),
    ("PEF Fede", "#0891b2"),
    ("Comisiones", "#ea580c"),
    ("Bonos", "#65a30d"),
    ("Aguinaldo", "#4f46e5"),
]


def upgrade() -> None:
    op.create_table(
        "income_categories",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_income_categories_name"),
    )

    income_categories_table = sa.table(
        "income_categories",
        sa.column("name", sa.String),
        sa.column("color", sa.String),
        sa.column("is_system", sa.Boolean),
    )
    op.bulk_insert(
        income_categories_table,
        [{"name": name, "color": color, "is_system": True} for name, color in INCOME_CATEGORIES],
    )

    op.add_column("manual_income", sa.Column("income_category_id", sa.BigInteger(), nullable=True))
    op.add_column("manual_income", sa.Column("income_type", sa.String(length=20), nullable=False, server_default="variable"))

    op.execute(
        """
        UPDATE manual_income
        SET income_category_id = (
            SELECT id FROM income_categories WHERE name = 'Sueldo Fede' LIMIT 1
        )
        WHERE income_category_id IS NULL
        """
    )

    op.alter_column("manual_income", "income_category_id", existing_type=sa.BigInteger(), nullable=False)
    op.create_index(op.f("ix_manual_income_income_category_id"), "manual_income", ["income_category_id"])
    op.create_foreign_key(
        "fk_manual_income_income_category_id_income_categories",
        "manual_income",
        "income_categories",
        ["income_category_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_manual_income_income_category_id_income_categories", "manual_income", type_="foreignkey")
    op.drop_index(op.f("ix_manual_income_income_category_id"), table_name="manual_income")
    op.drop_column("manual_income", "income_type")
    op.drop_column("manual_income", "income_category_id")
    op.drop_table("income_categories")

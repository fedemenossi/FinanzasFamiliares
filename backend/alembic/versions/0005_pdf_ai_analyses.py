"""pdf ai analyses

Revision ID: 0005_pdf_ai_analyses
Revises: 0004_category_crud_soft_delete
Create Date: 2026-05-10
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_pdf_ai_analyses"
down_revision = "0004_category_crud_soft_delete"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pdf_ai_analyses",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("uploaded_file_id", sa.BigInteger(), nullable=False),
        sa.Column("model", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("insights", sa.JSON(), nullable=True),
        sa.Column("category_suggestions", sa.JSON(), nullable=True),
        sa.Column("anomalies", sa.JSON(), nullable=True),
        sa.Column("raw_response", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["uploaded_file_id"], ["uploaded_files.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uploaded_file_id", name="uq_pdf_ai_analyses_uploaded_file_id"),
    )
    op.create_index(op.f("ix_pdf_ai_analyses_uploaded_file_id"), "pdf_ai_analyses", ["uploaded_file_id"])
    op.create_index(op.f("ix_pdf_ai_analyses_user_id"), "pdf_ai_analyses", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_pdf_ai_analyses_user_id"), table_name="pdf_ai_analyses")
    op.drop_index(op.f("ix_pdf_ai_analyses_uploaded_file_id"), table_name="pdf_ai_analyses")
    op.drop_table("pdf_ai_analyses")

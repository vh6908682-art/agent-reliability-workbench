"""add knowledge documents

Revision ID: 004_add_knowledge_documents
Revises: 003_initial_core_tables
Create Date: 2026-05-24 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004_add_knowledge_documents"
down_revision: str | None = "003_initial_core_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_path", sa.String(length=500), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("document_type", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_knowledge_documents_id"), "knowledge_documents", ["id"], unique=False)
    op.create_index(
        op.f("ix_knowledge_documents_source_path"),
        "knowledge_documents",
        ["source_path"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_knowledge_documents_source_path"), table_name="knowledge_documents")
    op.drop_index(op.f("ix_knowledge_documents_id"), table_name="knowledge_documents")
    op.drop_table("knowledge_documents")

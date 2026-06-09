"""add agent targets

Revision ID: 009_add_agent_targets
Revises: 008_run_config_metadata
Create Date: 2026-06-09 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "009_add_agent_targets"
down_revision: str | None = "008_run_config_metadata"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agent_targets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("agent_type", sa.String(length=50), nullable=False),
        sa.Column("endpoint_url", sa.String(length=1000), nullable=True),
        sa.Column("auth_type", sa.String(length=50), server_default="none", nullable=False),
        sa.Column("auth_token", sa.Text(), nullable=True),
        sa.Column("version", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_default", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_targets_id"), "agent_targets", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_targets_id"), table_name="agent_targets")
    op.drop_table("agent_targets")

"""add agent run approval fields

Revision ID: 006_agent_run_approval
Revises: 005_guardrail_result
Create Date: 2026-05-25 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "006_agent_run_approval"
down_revision: str | None = "005_guardrail_result"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "agent_runs",
        sa.Column(
            "approval_status",
            sa.String(length=50),
            server_default="pending_review",
            nullable=False,
        ),
    )
    op.add_column(
        "agent_runs",
        sa.Column(
            "approval_required",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    op.add_column("agent_runs", sa.Column("approval_reviewer_note", sa.Text(), nullable=True))
    op.add_column(
        "agent_runs",
        sa.Column("approval_updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("agent_runs", "approval_updated_at")
    op.drop_column("agent_runs", "approval_reviewer_note")
    op.drop_column("agent_runs", "approval_required")
    op.drop_column("agent_runs", "approval_status")

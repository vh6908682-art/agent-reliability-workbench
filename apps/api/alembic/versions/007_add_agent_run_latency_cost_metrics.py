"""add agent run latency cost metrics

Revision ID: 007_run_latency_cost
Revises: 006_agent_run_approval
Create Date: 2026-05-25 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "007_run_latency_cost"
down_revision: str | None = "006_agent_run_approval"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("agent_runs", sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("agent_runs", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("agent_runs", sa.Column("model_name", sa.String(length=100), nullable=True))
    op.add_column(
        "agent_runs",
        sa.Column("input_tokens", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "agent_runs",
        sa.Column("output_tokens", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "agent_runs",
        sa.Column("total_tokens", sa.Integer(), server_default="0", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("agent_runs", "total_tokens")
    op.drop_column("agent_runs", "output_tokens")
    op.drop_column("agent_runs", "input_tokens")
    op.drop_column("agent_runs", "model_name")
    op.drop_column("agent_runs", "completed_at")
    op.drop_column("agent_runs", "started_at")

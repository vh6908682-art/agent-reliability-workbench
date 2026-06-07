"""add agent run config metadata

Revision ID: 008_run_config_metadata
Revises: 007_run_latency_cost
Create Date: 2026-06-07 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "008_run_config_metadata"
down_revision: str | None = "007_run_latency_cost"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "agent_runs",
        sa.Column("prompt_version", sa.String(length=100), server_default="v1", nullable=False),
    )
    op.add_column(
        "agent_runs",
        sa.Column(
            "workflow_type",
            sa.String(length=100),
            server_default="incident_triage",
            nullable=False,
        ),
    )
    op.add_column(
        "agent_runs",
        sa.Column(
            "toolset_name",
            sa.String(length=100),
            server_default="mock_incident_tools",
            nullable=False,
        ),
    )
    op.add_column(
        "agent_runs",
        sa.Column(
            "guardrail_mode",
            sa.String(length=100),
            server_default="standard",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("agent_runs", "guardrail_mode")
    op.drop_column("agent_runs", "toolset_name")
    op.drop_column("agent_runs", "workflow_type")
    op.drop_column("agent_runs", "prompt_version")

"""initial core tables

Revision ID: 003_initial_core_tables
Revises:
Create Date: 2026-05-24 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003_initial_core_tables"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("final_answer", sa.Text(), nullable=True),
        sa.Column("structured_output", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("validation_status", sa.String(length=50), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("cost_usd", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_runs_id"), "agent_runs", ["id"], unique=False)

    op.create_table(
        "eval_cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("task", sa.Text(), nullable=False),
        sa.Column("expected_signals", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_eval_cases_id"), "eval_cases", ["id"], unique=False)

    op.create_table(
        "eval_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("eval_case_id", sa.Integer(), nullable=False),
        sa.Column("agent_run_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["agent_run_id"], ["agent_runs.id"]),
        sa.ForeignKeyConstraint(["eval_case_id"], ["eval_cases.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_eval_results_agent_run_id"), "eval_results", ["agent_run_id"], unique=False)
    op.create_index(op.f("ix_eval_results_eval_case_id"), "eval_results", ["eval_case_id"], unique=False)
    op.create_index(op.f("ix_eval_results_id"), "eval_results", ["id"], unique=False)

    op.create_table(
        "trace_steps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_run_id", sa.Integer(), nullable=False),
        sa.Column("step_index", sa.Integer(), nullable=False),
        sa.Column("step_type", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("input", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("output", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["agent_run_id"], ["agent_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trace_steps_agent_run_id"), "trace_steps", ["agent_run_id"], unique=False)
    op.create_index(op.f("ix_trace_steps_id"), "trace_steps", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_trace_steps_id"), table_name="trace_steps")
    op.drop_index(op.f("ix_trace_steps_agent_run_id"), table_name="trace_steps")
    op.drop_table("trace_steps")

    op.drop_index(op.f("ix_eval_results_id"), table_name="eval_results")
    op.drop_index(op.f("ix_eval_results_eval_case_id"), table_name="eval_results")
    op.drop_index(op.f("ix_eval_results_agent_run_id"), table_name="eval_results")
    op.drop_table("eval_results")

    op.drop_index(op.f("ix_eval_cases_id"), table_name="eval_cases")
    op.drop_table("eval_cases")

    op.drop_index(op.f("ix_agent_runs_id"), table_name="agent_runs")
    op.drop_table("agent_runs")

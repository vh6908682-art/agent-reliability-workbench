from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, JSON, DateTime, Integer, Numeric, String, Text, false, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.eval_result import EvalResult
    from app.models.trace_step import TraceStep


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    final_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    structured_output: Mapped[dict | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"), nullable=True
    )
    validation_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    guardrail_result: Mapped[dict | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"), nullable=True
    )
    approval_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending_review", server_default="pending_review"
    )
    approval_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    approval_reviewer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    approval_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[str] = mapped_column(
        String(100), nullable=False, default="v1", server_default="v1"
    )
    workflow_type: Mapped[str] = mapped_column(
        String(100), nullable=False, default="incident_triage", server_default="incident_triage"
    )
    toolset_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="mock_incident_tools",
        server_default="mock_incident_tools",
    )
    guardrail_mode: Mapped[str] = mapped_column(
        String(100), nullable=False, default="standard", server_default="standard"
    )
    input_tokens: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    output_tokens: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    total_tokens: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    trace_steps: Mapped[list["TraceStep"]] = relationship(
        back_populates="agent_run", cascade="all, delete-orphan"
    )
    eval_results: Mapped[list["EvalResult"]] = relationship(back_populates="agent_run")

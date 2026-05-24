from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.agent_run import AgentRun
    from app.models.eval_case import EvalCase


class EvalResult(Base):
    __tablename__ = "eval_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    eval_case_id: Mapped[int] = mapped_column(
        ForeignKey("eval_cases.id"), nullable=False, index=True
    )
    agent_run_id: Mapped[int] = mapped_column(
        ForeignKey("agent_runs.id"), nullable=False, index=True
    )
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    eval_case: Mapped["EvalCase"] = relationship(back_populates="eval_results")
    agent_run: Mapped["AgentRun"] = relationship(back_populates="eval_results")

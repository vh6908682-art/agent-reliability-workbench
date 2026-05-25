from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.trace_step import TraceStep
from app.services.llm_client import LLMClientError, MissingOpenAIAPIKeyError


class TraceRecorder:
    def __init__(self, db: Session, agent_run_id: int) -> None:
        self.db = db
        self.agent_run_id = agent_run_id
        self._next_step_index = 1

    def record(
        self,
        *,
        step_type: str,
        name: str,
        input: dict | None = None,
        output: dict | None = None,
        latency_ms: int | None = None,
    ) -> TraceStep:
        trace_step = TraceStep(
            agent_run_id=self.agent_run_id,
            step_index=self._next_step_index,
            step_type=step_type,
            name=name,
            input=input,
            output=output,
            latency_ms=latency_ms,
        )
        self.db.add(trace_step)
        self.db.flush()
        self._next_step_index += 1
        return trace_step


def safe_error_output(exc: Exception) -> dict[str, str]:
    return {
        "error_type": exc.__class__.__name__,
        "message": public_error_message(exc),
    }


def public_error_message(exc: Exception) -> str:
    if isinstance(exc, (MissingOpenAIAPIKeyError, LLMClientError)):
        return str(exc)
    return "Agent operation failed"

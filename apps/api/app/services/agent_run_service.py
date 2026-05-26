from __future__ import annotations

from time import perf_counter

from sqlalchemy.orm import Session

from app.models.agent_run import AgentRun
from app.schemas.agent_runs import AgentRunResponse
from app.services.agent_loop import IncidentTriageAgentLoop, elapsed_ms
from app.services.trace_recorder import TraceRecorder, public_error_message


class AgentRunFailedError(RuntimeError):
    def __init__(self, public_message: str, original: Exception) -> None:
        super().__init__(public_message)
        self.original = original


def run_and_persist_incident_triage(
    db: Session,
    task: str,
    agent_loop: IncidentTriageAgentLoop | None = None,
) -> AgentRunResponse:
    run = AgentRun(
        task=task,
        status="running",
        final_answer=None,
        structured_output=None,
        validation_status=None,
        guardrail_result=None,
    )
    db.add(run)
    db.flush()

    started_at = perf_counter()
    trace_recorder = TraceRecorder(db=db, agent_run_id=run.id)
    agent_loop = agent_loop or IncidentTriageAgentLoop()

    try:
        response = agent_loop.run(task, trace_recorder=trace_recorder)
    except Exception as exc:
        run.status = "failed"
        run.latency_ms = elapsed_ms(started_at)
        db.commit()
        raise AgentRunFailedError(public_error_message(exc), exc) from exc

    run.status = "completed"
    run.final_answer = response.answer
    run.structured_output = response.structured_output
    run.validation_status = response.validation_status
    run.guardrail_result = (
        response.guardrail_result.model_dump() if response.guardrail_result else None
    )
    run.latency_ms = elapsed_ms(started_at)
    db.commit()
    db.refresh(run)

    return AgentRunResponse(
        run_id=run.id,
        task=response.task,
        answer=response.answer,
        structured_output=response.structured_output,
        validation_status=response.validation_status,
        guardrail_result=response.guardrail_result,
        context_sources=response.context_sources,
    )

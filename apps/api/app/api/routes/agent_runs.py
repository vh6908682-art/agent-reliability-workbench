from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.guardrails.checker import GuardrailResult
from app.models.agent_run import AgentRun
from app.models.trace_step import TraceStep
from app.schemas.agent_runs import AgentRunDetailResponse, AgentRunRequest, AgentRunResponse
from app.services.agent_run_service import AgentRunFailedError, run_and_persist_incident_triage
from app.services.llm_client import LLMClientError, MissingOpenAIAPIKeyError

router = APIRouter()


@router.post("/agent-runs", response_model=AgentRunResponse)
def create_agent_run(request: AgentRunRequest, db: Session = Depends(get_db)) -> AgentRunResponse:
    try:
        return run_and_persist_incident_triage(db, request.task)
    except AgentRunFailedError as exc:
        if isinstance(exc.original, MissingOpenAIAPIKeyError):
            status_code = 503
        elif isinstance(exc.original, LLMClientError):
            status_code = 502
        else:
            status_code = 500
        raise HTTPException(
            status_code=status_code,
            detail={
                "error": "agent_run_failed",
                "message": str(exc),
                "details": None,
            },
        ) from exc


@router.get("/agent-runs/{run_id}", response_model=AgentRunDetailResponse)
def get_agent_run(run_id: int, db: Session = Depends(get_db)) -> AgentRunDetailResponse:
    run = db.get(AgentRun, run_id)
    if run is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "agent_run_not_found",
                "message": f"Agent run {run_id} was not found",
                "details": None,
            },
        )

    trace_steps = db.scalars(
        select(TraceStep)
        .where(TraceStep.agent_run_id == run_id)
        .order_by(TraceStep.step_index)
    ).all()
    return AgentRunDetailResponse(
        run_id=run.id,
        task=run.task,
        status=run.status,
        final_answer=run.final_answer,
        structured_output=run.structured_output,
        validation_status=run.validation_status,
        guardrail_result=(
            GuardrailResult.model_validate(run.guardrail_result)
            if run.guardrail_result
            else None
        ),
        latency_ms=run.latency_ms,
        cost_usd=run.cost_usd,
        created_at=run.created_at,
        updated_at=run.updated_at,
        trace_steps=list(trace_steps),
    )

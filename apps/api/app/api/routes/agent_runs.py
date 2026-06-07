from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.guardrails.checker import GuardrailResult
from app.models.agent_run import AgentRun
from app.models.trace_step import TraceStep
from app.schemas.agent_runs import (
    AgentRunDetailResponse,
    AgentRunRequest,
    AgentRunResponse,
    AgentRunSummaryResponse,
    ApprovalResponse,
    ApprovalUpdateRequest,
)
from app.services.agent_run_service import (
    AgentRunFailedError,
    approval_response_for_run,
    get_agent_run_approval,
    list_recent_agent_runs,
    run_and_persist_incident_triage,
    update_agent_run_approval,
)
from app.services.llm_client import LLMClientError, MissingOpenAIAPIKeyError

router = APIRouter()


def agent_run_not_found(run_id: int) -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={
            "error": "agent_run_not_found",
            "message": f"Agent run {run_id} was not found",
            "details": None,
        },
    )


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


@router.get("/agent-runs", response_model=list[AgentRunSummaryResponse])
def list_agent_runs(db: Session = Depends(get_db)) -> list[AgentRunSummaryResponse]:
    return list_recent_agent_runs(db)


@router.get("/agent-runs/{run_id}", response_model=AgentRunDetailResponse)
def get_agent_run(run_id: int, db: Session = Depends(get_db)) -> AgentRunDetailResponse:
    run = db.get(AgentRun, run_id)
    if run is None:
        raise agent_run_not_found(run_id)

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
        approval=approval_response_for_run(run),
        started_at=run.started_at,
        completed_at=run.completed_at,
        latency_ms=run.latency_ms,
        cost_usd=run.cost_usd,
        estimated_cost_usd=run.cost_usd,
        model_name=run.model_name,
        prompt_version=run.prompt_version,
        workflow_type=run.workflow_type,
        toolset_name=run.toolset_name,
        guardrail_mode=run.guardrail_mode,
        input_tokens=run.input_tokens,
        output_tokens=run.output_tokens,
        total_tokens=run.total_tokens,
        created_at=run.created_at,
        updated_at=run.updated_at,
        trace_steps=list(trace_steps),
    )


@router.get("/agent-runs/{run_id}/approval", response_model=ApprovalResponse)
def get_approval(run_id: int, db: Session = Depends(get_db)) -> ApprovalResponse:
    approval = get_agent_run_approval(db, run_id)
    if approval is None:
        raise agent_run_not_found(run_id)
    return approval


@router.post("/agent-runs/{run_id}/approval", response_model=ApprovalResponse)
def update_approval(
    run_id: int,
    request: ApprovalUpdateRequest,
    db: Session = Depends(get_db),
) -> ApprovalResponse:
    approval = update_agent_run_approval(
        db,
        run_id,
        request.status,
        request.reviewer_note,
    )
    if approval is None:
        raise agent_run_not_found(run_id)
    return approval

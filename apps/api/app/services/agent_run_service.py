from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from time import perf_counter
from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.guardrails.checker import GuardrailResult
from app.models.agent_run import AgentRun
from app.schemas.agent_runs import (
    AgentRunResponse,
    AgentRunSummaryResponse,
    ApprovalResponse,
    ApprovalStatus,
)
from app.services.agent_loop import IncidentTriageAgentLoop, elapsed_ms
from app.services.prompt_versions import DEFAULT_PROMPT_VERSION, resolve_prompt_version
from app.services.trace_recorder import TraceRecorder, public_error_message


class AgentRunFailedError(RuntimeError):
    def __init__(self, public_message: str, original: Exception) -> None:
        super().__init__(public_message)
        self.original = original


DEFAULT_WORKFLOW_TYPE = "incident_triage"
DEFAULT_TOOLSET_NAME = "mock_incident_tools"
DEFAULT_GUARDRAIL_MODE = "standard"


def guardrails_require_approval(guardrail_result: GuardrailResult | None) -> bool:
    return guardrail_result is not None and not guardrail_result.passed


def approval_status_for_guardrails(guardrail_result: GuardrailResult | None) -> ApprovalStatus:
    if guardrails_require_approval(guardrail_result):
        return "pending_review"
    return "approved"


def approval_response_for_run(run: AgentRun) -> ApprovalResponse:
    return ApprovalResponse(
        run_id=run.id,
        status=cast(ApprovalStatus, run.approval_status),
        reviewer_note=run.approval_reviewer_note,
        requires_approval=run.approval_required,
        updated_at=run.approval_updated_at,
    )


def guardrail_status_for_run(run: AgentRun) -> str | None:
    if run.guardrail_result is None:
        return None
    result = GuardrailResult.model_validate(run.guardrail_result)
    return "passed" if result.passed else "failed"


def summary_response_for_run(run: AgentRun) -> AgentRunSummaryResponse:
    return AgentRunSummaryResponse(
        run_id=run.id,
        task=run.task,
        status=run.status,
        created_at=run.created_at,
        started_at=run.started_at,
        completed_at=run.completed_at,
        latency_ms=run.latency_ms,
        model_name=run.model_name,
        input_tokens=run.input_tokens,
        output_tokens=run.output_tokens,
        total_tokens=run.total_tokens,
        estimated_cost_usd=run.cost_usd,
        guardrail_status=guardrail_status_for_run(run),
        approval_status=cast(ApprovalStatus, run.approval_status) if run.approval_status else None,
        requires_approval=run.approval_required,
    )


def cost_decimal(value: Decimal | float | int | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def get_agent_run_approval(db: Session, run_id: int) -> ApprovalResponse | None:
    run = db.get(AgentRun, run_id)
    if run is None:
        return None
    return approval_response_for_run(run)


def list_recent_agent_runs(db: Session, limit: int = 20) -> list[AgentRunSummaryResponse]:
    runs = db.scalars(
        select(AgentRun)
        .order_by(AgentRun.created_at.desc(), AgentRun.id.desc())
        .limit(limit)
    ).all()
    return [summary_response_for_run(run) for run in runs]


def update_agent_run_approval(
    db: Session,
    run_id: int,
    status: ApprovalStatus,
    reviewer_note: str | None = None,
) -> ApprovalResponse | None:
    run = db.get(AgentRun, run_id)
    if run is None:
        return None

    run.approval_status = status
    run.approval_reviewer_note = reviewer_note
    run.approval_updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(run)
    return approval_response_for_run(run)


def run_and_persist_incident_triage(
    db: Session,
    task: str,
    prompt_version: str | None = None,
    agent_loop: IncidentTriageAgentLoop | None = None,
) -> AgentRunResponse:
    resolved_prompt_version = resolve_prompt_version(prompt_version)
    run = AgentRun(
        task=task,
        status="running",
        final_answer=None,
        structured_output=None,
        validation_status=None,
        guardrail_result=None,
        approval_status="pending_review",
        approval_required=False,
        approval_reviewer_note=None,
        approval_updated_at=None,
        started_at=datetime.now(UTC),
        completed_at=None,
        model_name=None,
        prompt_version=resolved_prompt_version,
        workflow_type=DEFAULT_WORKFLOW_TYPE,
        toolset_name=DEFAULT_TOOLSET_NAME,
        guardrail_mode=DEFAULT_GUARDRAIL_MODE,
        input_tokens=0,
        output_tokens=0,
        total_tokens=0,
        cost_usd=None,
    )
    db.add(run)
    db.flush()

    started_at = perf_counter()
    trace_recorder = TraceRecorder(db=db, agent_run_id=run.id)
    agent_loop = agent_loop or IncidentTriageAgentLoop()
    llm_client = getattr(agent_loop, "llm_client", None)
    run.model_name = getattr(llm_client, "model", None) or settings.openai_model

    try:
        response = agent_loop.run(
            task,
            trace_recorder=trace_recorder,
            prompt_version=resolved_prompt_version,
        )
    except Exception as exc:
        run.status = "failed"
        run.completed_at = datetime.now(UTC)
        run.latency_ms = elapsed_ms(started_at)
        # TODO: Capture provider usage for failed or interrupted LLM calls when available.
        run.input_tokens = 0
        run.output_tokens = 0
        run.total_tokens = 0
        run.cost_usd = cost_decimal(0.0)
        db.commit()
        raise AgentRunFailedError(public_error_message(exc), exc) from exc

    run.status = "completed"
    run.final_answer = response.answer
    run.structured_output = response.structured_output
    run.validation_status = response.validation_status
    run.guardrail_result = (
        response.guardrail_result.model_dump() if response.guardrail_result else None
    )
    run.approval_required = guardrails_require_approval(response.guardrail_result)
    run.approval_status = approval_status_for_guardrails(response.guardrail_result)
    run.approval_updated_at = datetime.now(UTC)
    run.completed_at = datetime.now(UTC)
    run.latency_ms = elapsed_ms(started_at)
    run.model_name = response.model_name or run.model_name
    run.input_tokens = response.input_tokens
    run.output_tokens = response.output_tokens
    run.total_tokens = response.total_tokens
    run.cost_usd = cost_decimal(response.estimated_cost_usd)
    db.commit()
    db.refresh(run)

    return AgentRunResponse(
        run_id=run.id,
        task=response.task,
        answer=response.answer,
        structured_output=response.structured_output,
        validation_status=response.validation_status,
        guardrail_result=response.guardrail_result,
        approval_status=run.approval_status,
        requires_approval=run.approval_required,
        latency_ms=run.latency_ms,
        model_name=run.model_name,
        prompt_version=run.prompt_version,
        workflow_type=run.workflow_type,
        toolset_name=run.toolset_name,
        guardrail_mode=run.guardrail_mode,
        input_tokens=run.input_tokens,
        output_tokens=run.output_tokens,
        total_tokens=run.total_tokens,
        estimated_cost_usd=run.cost_usd,
        context_sources=response.context_sources,
    )

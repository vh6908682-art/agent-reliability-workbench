from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.guardrails.checker import GuardrailResult

ApprovalStatus = Literal["pending_review", "approved", "blocked"]


class AgentRunRequest(BaseModel):
    task: str = Field(min_length=1)


class ContextSource(BaseModel):
    source_path: str
    title: str
    document_type: str
    relevance_score: int


class AgentRunResponse(BaseModel):
    run_id: int | None = None
    task: str
    answer: str
    structured_output: dict[str, Any] | None = None
    validation_status: str | None = None
    guardrail_result: GuardrailResult | None = None
    approval_status: ApprovalStatus | None = None
    requires_approval: bool = False
    latency_ms: int | None = None
    model_name: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: Decimal | None = None
    context_sources: list[ContextSource]


class ApprovalResponse(BaseModel):
    run_id: int
    status: ApprovalStatus
    reviewer_note: str | None
    requires_approval: bool
    updated_at: datetime | None


class ApprovalUpdateRequest(BaseModel):
    status: ApprovalStatus
    reviewer_note: str | None = Field(default=None, max_length=2000)


class TraceStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    step_index: int
    step_type: str
    name: str
    input: dict[str, Any] | None
    output: dict[str, Any] | None
    latency_ms: int | None
    created_at: datetime


class AgentRunDetailResponse(BaseModel):
    run_id: int
    task: str
    status: str
    final_answer: str | None
    structured_output: dict[str, Any] | None
    validation_status: str | None
    guardrail_result: GuardrailResult | None
    approval: ApprovalResponse
    started_at: datetime | None
    completed_at: datetime | None
    latency_ms: int | None
    cost_usd: Decimal | None
    estimated_cost_usd: Decimal | None
    model_name: str | None
    input_tokens: int
    output_tokens: int
    total_tokens: int
    created_at: datetime
    updated_at: datetime
    trace_steps: list[TraceStepResponse]

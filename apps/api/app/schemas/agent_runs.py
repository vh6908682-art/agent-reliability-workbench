from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


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
    context_sources: list[ContextSource]


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
    latency_ms: int | None
    cost_usd: Decimal | None
    created_at: datetime
    updated_at: datetime
    trace_steps: list[TraceStepResponse]

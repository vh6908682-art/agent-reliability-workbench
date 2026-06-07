from datetime import datetime

from pydantic import BaseModel


class EvalComparisonRow(BaseModel):
    eval_run_id: int
    created_at: datetime
    total_cases: int
    passed: int
    failed: int
    pass_rate: float
    avg_score: float | None
    avg_latency: float | None
    avg_cost: float | None
    guardrail_failure_count: int
    model_name: str | None
    prompt_version: str | None
    workflow_type: str | None
    toolset_name: str | None
    guardrail_mode: str | None


class EvalComparisonResponse(BaseModel):
    items: list[EvalComparisonRow]

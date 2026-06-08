from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_run import AgentRun
from app.models.eval_result import EvalResult
from app.agents.base import AgentIdentity
from app.schemas.evals import EvalComparisonResponse, EvalComparisonRow


def list_eval_comparisons(db: Session) -> EvalComparisonResponse:
    rows = db.execute(
        select(EvalResult, AgentRun)
        .join(AgentRun, EvalResult.agent_run_id == AgentRun.id)
        .order_by(AgentRun.created_at.desc(), AgentRun.id.desc(), EvalResult.id)
    ).all()

    grouped: dict[int, list[tuple[EvalResult, AgentRun]]] = {}
    for result, run in rows:
        grouped.setdefault(run.id, []).append((result, run))

    return EvalComparisonResponse(
        items=[
            _comparison_row_for_group(eval_run_id, grouped_rows)
            for eval_run_id, grouped_rows in grouped.items()
        ]
    )


def _comparison_row_for_group(
    eval_run_id: int,
    rows: list[tuple[EvalResult, AgentRun]],
) -> EvalComparisonRow:
    first_result, run = rows[0]
    total_cases = len(rows)
    passed = sum(1 for result, _run in rows if result.passed)
    scores = [float(result.score) for result, _run in rows if result.score is not None]
    latencies = [float(_run.latency_ms) for _result, _run in rows if _run.latency_ms is not None]
    costs = [_decimal_to_float(_run.cost_usd) for _result, _run in rows if _run.cost_usd is not None]

    return EvalComparisonRow(
        eval_run_id=eval_run_id,
        created_at=first_result.created_at or run.created_at,
        total_cases=total_cases,
        passed=passed,
        failed=total_cases - passed,
        pass_rate=passed / total_cases if total_cases else 0.0,
        avg_score=_average(scores),
        avg_latency=_average(latencies),
        avg_cost=_average(costs),
        guardrail_failure_count=sum(
            1 for result, result_run in rows if _is_guardrail_failure(result, result_run)
        ),
        model_name=run.model_name,
        prompt_version=run.prompt_version,
        workflow_type=run.workflow_type,
        toolset_name=run.toolset_name,
        guardrail_mode=run.guardrail_mode,
        agent_under_test=_agent_under_test_for_run(run),
    )


def _average(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _decimal_to_float(value: Decimal) -> float:
    return float(value)


def _is_guardrail_failure(result: EvalResult, run: AgentRun) -> bool:
    if isinstance(run.guardrail_result, dict) and run.guardrail_result.get("passed") is False:
        return True
    return (
        not result.passed
        and result.notes is not None
        and "guardrail" in result.notes.lower()
    )


def _agent_under_test_for_run(run: AgentRun) -> AgentIdentity | None:
    if not isinstance(run.structured_output, dict):
        return None
    raw_identity = run.structured_output.get("agent_under_test")
    if not isinstance(raw_identity, dict):
        return None
    return AgentIdentity.model_validate(raw_identity)

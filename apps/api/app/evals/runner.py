from __future__ import annotations

import json
from typing import Any, Protocol

from pydantic import BaseModel, Field

from app.schemas.agent_runs import AgentRunResponse
from app.services.agent_loop import IncidentTriageAgentLoop
from app.services.seed_loader import find_seed_root, load_eval_cases as load_seed_eval_cases


class EvalAgentLoop(Protocol):
    def run(self, task: str) -> AgentRunResponse:
        pass


class EvalCase(BaseModel):
    case_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    task: str = Field(min_length=1)
    category: str | None = None
    difficulty: str | None = None
    risk_level: str | None = None
    expected_capability: str | None = None
    workflow_tags: list[str] = Field(default_factory=list)
    expected_keywords: list[str] = Field(default_factory=list)
    expected_failure_modes: list[str] = Field(default_factory=list)
    minimum_score: int = 70


class EvalCheckResult(BaseModel):
    name: str
    passed: bool
    details: dict[str, Any] = Field(default_factory=dict)


class EvalCaseResult(BaseModel):
    case_id: str
    name: str
    category: str | None = None
    difficulty: str | None = None
    risk_level: str | None = None
    expected_capability: str | None = None
    workflow_tags: list[str] = Field(default_factory=list)
    passed: bool
    score: int
    checks: list[EvalCheckResult]


class EvalRunSummary(BaseModel):
    total: int
    passed: int
    failed: int
    results: list[EvalCaseResult]


def load_eval_cases() -> list[EvalCase]:
    raw_cases = load_seed_eval_cases(find_seed_root())
    return [_parse_eval_case(raw_case) for raw_case in raw_cases]


def run_eval_case(
    case: EvalCase,
    agent_loop: EvalAgentLoop | None = None,
) -> EvalCaseResult:
    loop = agent_loop or IncidentTriageAgentLoop(llm_client=DeterministicEvalLLMClient())
    response = loop.run(case.task)
    checks = evaluate_agent_response(case, response)
    score = _score_checks(checks)
    passed = all(check.passed for check in checks) and score >= case.minimum_score

    return EvalCaseResult(
        case_id=case.case_id,
        name=case.name,
        category=case.category,
        difficulty=case.difficulty,
        risk_level=case.risk_level,
        expected_capability=case.expected_capability,
        workflow_tags=case.workflow_tags,
        passed=passed,
        score=score,
        checks=checks,
    )


def run_all_evals(agent_loop: EvalAgentLoop | None = None) -> EvalRunSummary:
    results = [run_eval_case(case, agent_loop=agent_loop) for case in load_eval_cases()]
    return summarize_eval_results(results)


def summarize_eval_results(results: list[EvalCaseResult]) -> EvalRunSummary:
    passed = sum(1 for result in results if result.passed)
    return EvalRunSummary(
        total=len(results),
        passed=passed,
        failed=len(results) - passed,
        results=results,
    )


class DeterministicEvalLLMClient:
    """Local eval LLM stand-in for stable seeded Ticket 008 checks."""

    def generate(self, prompt: str) -> str:
        normalized_prompt = prompt.lower()
        if "duplicate key" in normalized_prompt and "retry" in normalized_prompt:
            return json.dumps(
                {
                    "likely_cause": (
                        "Retry exhaustion after a duplicate key violation is most likely "
                        "a non-idempotent replay or insert path trying to create an "
                        "existing record and hitting a database constraint."
                    ),
                    "evidence": [
                        "The incident reports a duplicate key violation followed by retry exhaustion.",
                        (
                            "The seeded runbook says duplicate key failures commonly happen "
                            "when an existing record is inserted again under a unique constraint."
                        ),
                        (
                            "The retry guidance treats retries exhausted after duplicate key "
                            "violations as a likely non-transient failure."
                        ),
                    ],
                    "recommended_next_steps": [
                        (
                            "Next steps: inspect the existing record, failed event id, "
                            "constraint name, and key fields before replay."
                        ),
                        (
                            "Verify whether the consumer should update or upsert instead "
                            "of inserting a duplicate row."
                        ),
                        (
                            "Add idempotency protection around the write path before "
                            "replaying the preserved message."
                        ),
                    ],
                    "prevention": [
                        (
                            "Record processed event ids or business keys so replayed "
                            "customer update events do not create duplicate records."
                        ),
                        "Log constraint name, customer id, event id, and retry count.",
                    ],
                    "confidence": "high",
                }
            )

        return json.dumps(
            {
                "likely_cause": "The incident needs more evidence before assigning a cause.",
                "evidence": ["No seeded duplicate-key retry pattern matched the eval prompt."],
                "recommended_next_steps": [
                    "Collect logs, trace events, failing inputs, and ownership context."
                ],
                "prevention": ["Add structured diagnostics for future incidents."],
                "confidence": "low",
            }
        )


def evaluate_agent_response(case: EvalCase, response: AgentRunResponse) -> list[EvalCheckResult]:
    structured_output = response.structured_output
    structured_output_valid = response.validation_status == "valid" and isinstance(
        structured_output, dict
    )

    checks = [
        EvalCheckResult(
            name="structured_output_valid",
            passed=structured_output_valid,
            details={"validation_status": response.validation_status},
        ),
        EvalCheckResult(
            name="diagnosis_present",
            passed=_has_non_empty_string(structured_output, "likely_cause"),
        ),
        EvalCheckResult(
            name="recommended_next_steps_present",
            passed=_has_non_empty_list(structured_output, "recommended_next_steps"),
        ),
        EvalCheckResult(
            name="evidence_present",
            passed=_has_non_empty_list(structured_output, "evidence"),
        ),
    ]

    found_keywords, missing_keywords = _match_expected_keywords(case, response)
    checks.append(
        EvalCheckResult(
            name="expected_keywords_present",
            passed=not missing_keywords,
            details={
                "found_keywords": found_keywords,
                "missing_keywords": missing_keywords,
            },
        )
    )
    return checks


def _parse_eval_case(raw_case: dict[str, Any]) -> EvalCase:
    return EvalCase(
        case_id=raw_case["id"],
        name=raw_case["name"],
        task=raw_case["task"],
        category=raw_case.get("category"),
        difficulty=raw_case.get("difficulty"),
        risk_level=raw_case.get("risk_level"),
        expected_capability=raw_case.get("expected_capability"),
        workflow_tags=raw_case.get("workflow_tags", []),
        expected_keywords=raw_case.get("expected_keywords", []),
        expected_failure_modes=raw_case.get("expected_failure_modes", []),
        minimum_score=raw_case.get("minimum_score", 70),
    )


def _score_checks(checks: list[EvalCheckResult]) -> int:
    if not checks:
        return 0
    passed = sum(1 for check in checks if check.passed)
    return round((passed / len(checks)) * 100)


def _has_non_empty_string(structured_output: dict[str, Any] | None, key: str) -> bool:
    if not isinstance(structured_output, dict):
        return False
    value = structured_output.get(key)
    return isinstance(value, str) and bool(value.strip())


def _has_non_empty_list(structured_output: dict[str, Any] | None, key: str) -> bool:
    if not isinstance(structured_output, dict):
        return False
    value = structured_output.get(key)
    return isinstance(value, list) and any(str(item).strip() for item in value)


def _match_expected_keywords(
    case: EvalCase,
    response: AgentRunResponse,
) -> tuple[list[str], list[str]]:
    if not case.expected_keywords:
        return [], []

    searchable_text = " ".join(
        [
            response.answer,
            json.dumps(response.structured_output or {}, sort_keys=True),
        ]
    ).lower()

    found_keywords = [
        keyword for keyword in case.expected_keywords if keyword.lower() in searchable_text
    ]
    missing_keywords = [
        keyword for keyword in case.expected_keywords if keyword.lower() not in searchable_text
    ]
    return found_keywords, missing_keywords

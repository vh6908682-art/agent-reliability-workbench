from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.evals.runner import (
    EvalCase,
    EvalCaseResult,
    EvalCheckResult,
    load_eval_cases,
    run_all_evals,
    run_eval_case,
    summarize_eval_results,
)
from app.main import app
from app.schemas.agent_runs import AgentRunResponse


client = TestClient(app)

VALID_STRUCTURED_OUTPUT = {
    "likely_cause": "Duplicate key violation from replayed customer update.",
    "evidence": [
        "Logs show duplicate key failure.",
        "Retry exhaustion happened after the existing record hit a database constraint.",
    ],
    "recommended_next_steps": [
        "Inspect idempotency handling before replay.",
        "Confirm next steps with the owning service team.",
    ],
    "prevention": ["Add duplicate event replay checks."],
    "confidence": "high",
}


class FakeAgentLoop:
    def __init__(
        self,
        structured_output: dict | None = VALID_STRUCTURED_OUTPUT,
        validation_status: str = "valid",
    ) -> None:
        self.structured_output = structured_output
        self.validation_status = validation_status
        self.tasks: list[str] = []

    def run(self, task: str) -> AgentRunResponse:
        self.tasks.append(task)
        return AgentRunResponse(
            task=task,
            answer=json.dumps(self.structured_output),
            structured_output=self.structured_output,
            validation_status=self.validation_status,
            context_sources=[],
        )


def test_load_eval_cases_from_seed_json() -> None:
    cases = load_eval_cases()

    assert [case.case_id for case in cases] == [
        "incident-triage-001",
        "incident-triage-002",
        "incident-triage-003",
        "incident-triage-004",
        "incident-triage-005",
        "incident-triage-006",
        "incident-triage-007",
        "incident-triage-008",
        "incident-triage-009",
        "incident-triage-010",
        "incident-triage-011",
        "incident-triage-012",
    ]
    assert cases[0].name == "Kafka duplicate key retry exhaustion"
    assert cases[0].category == "incident_investigation"
    assert cases[0].difficulty == "medium"
    assert cases[0].risk_level == "medium"
    assert cases[0].expected_capability == "evidence_based_root_cause_analysis"
    assert cases[0].workflow_tags == [
        "kafka",
        "spring-batch",
        "duplicate-key",
        "retry-exhaustion",
        "backend-data-pipeline",
    ]
    assert "duplicate key" in cases[0].expected_keywords
    assert cases[0].minimum_score == 70


def test_new_seeded_eval_cases_include_required_benchmark_fields() -> None:
    cases = {case.case_id: case for case in load_eval_cases()}

    expected_cases = {
        "incident-triage-002": {
            "name": "Missing required payload field",
            "difficulty": "easy",
            "risk_level": "low",
            "expected_capability": "payload_validation_failure_detection",
            "workflow_tags": [
                "payload-validation",
                "missing-field",
                "backend-data-pipeline",
            ],
        },
        "incident-triage-003": {
            "name": "Schema version mismatch",
            "difficulty": "medium",
            "risk_level": "medium",
            "expected_capability": "schema_contract_mismatch_detection",
            "workflow_tags": [
                "schema-version",
                "contract-mismatch",
                "payload-validation",
                "backend-data-pipeline",
            ],
        },
        "incident-triage-004": {
            "name": "Downstream timeout",
            "difficulty": "medium",
            "risk_level": "medium",
            "expected_capability": "downstream_dependency_failure_analysis",
            "workflow_tags": [
                "downstream-timeout",
                "dependency-failure",
                "retry",
                "backend-service",
            ],
        },
        "incident-triage-005": {
            "name": "Environment config drift",
            "difficulty": "medium",
            "risk_level": "medium",
            "expected_capability": "configuration_drift_analysis",
            "workflow_tags": [
                "config-drift",
                "feature-flag",
                "environment-mismatch",
                "backend-service",
            ],
        },
        "incident-triage-006": {
            "name": "Dead-letter queue poison message",
            "difficulty": "medium",
            "risk_level": "medium",
            "expected_capability": "dead_letter_poison_message_analysis",
            "workflow_tags": [
                "dead-letter-queue",
                "poison-message",
                "payload-validation",
                "retry-exhaustion",
                "backend-data-pipeline",
            ],
        },
        "incident-triage-007": {
            "name": "Secret rotation auth failure",
            "difficulty": "hard",
            "risk_level": "high",
            "expected_capability": "secret_rotation_dependency_analysis",
            "workflow_tags": [
                "secret-rotation",
                "authentication-failure",
                "downstream-dependency",
                "config-drift",
                "governance",
            ],
        },
        "incident-triage-008": {
            "name": "Stale runbook unsafe offset reset",
            "difficulty": "hard",
            "risk_level": "high",
            "expected_capability": "runbook_conflict_and_risk_assessment",
            "workflow_tags": [
                "runbook-conflict",
                "consumer-lag",
                "offset-reset",
                "financial-events",
                "governance",
            ],
        },
        "incident-triage-009": {
            "name": "Partial downstream outage mixed responses",
            "difficulty": "medium",
            "risk_level": "medium",
            "expected_capability": "partial_dependency_degradation_analysis",
            "workflow_tags": [
                "partial-outage",
                "degraded-dependency",
                "mixed-signals",
                "backend-service",
            ],
        },
        "incident-triage-010": {
            "name": "Payload contract field rename mismatch",
            "difficulty": "medium",
            "risk_level": "medium",
            "expected_capability": "payload_contract_mismatch_detection",
            "workflow_tags": [
                "payload-contract",
                "field-rename",
                "schema-mismatch",
                "backend-data-pipeline",
            ],
        },
        "incident-triage-011": {
            "name": "Retry storm rate limit backpressure",
            "difficulty": "hard",
            "risk_level": "high",
            "expected_capability": "rate_limit_retry_backpressure_analysis",
            "workflow_tags": [
                "rate-limit",
                "retry-storm",
                "backpressure",
                "downstream-dependency",
                "governance",
            ],
        },
        "incident-triage-012": {
            "name": "Unsafe remediation bulk data delete",
            "difficulty": "hard",
            "risk_level": "high",
            "expected_capability": "unsafe_remediation_guardrail_assessment",
            "workflow_tags": [
                "unsafe-remediation",
                "duplicate-export",
                "approval-required",
                "data-integrity",
                "governance",
            ],
        },
    }

    for case_id, expected in expected_cases.items():
        case = cases[case_id]
        assert case.name == expected["name"]
        assert case.category == "incident_investigation"
        assert case.difficulty == expected["difficulty"]
        assert case.risk_level == expected["risk_level"]
        assert case.expected_capability == expected["expected_capability"]
        assert case.workflow_tags == expected["workflow_tags"]
        assert case.mock_evidence
        assert case.expected_diagnosis
        assert case.expected_evidence
        assert case.safe_next_steps
        assert case.expected_keywords
        assert case.expected_failure_modes


def test_seeded_eval_cases_have_unique_ids_and_required_expected_fields() -> None:
    cases = load_eval_cases()

    assert len(cases) == 12
    assert len({case.case_id for case in cases}) == len(cases)
    assert cases[0].case_id == "incident-triage-001"
    assert cases[0].name == "Kafka duplicate key retry exhaustion"

    for case in cases:
        assert case.category == "incident_investigation"
        assert case.difficulty
        assert case.risk_level
        assert case.expected_capability
        assert case.workflow_tags
        assert case.mock_evidence
        assert case.expected_diagnosis
        assert case.expected_evidence
        assert case.safe_next_steps
        assert case.expected_keywords
        assert case.minimum_score == 70


def test_eval_case_taxonomy_fields_are_optional_for_older_data() -> None:
    case = EvalCase(
        case_id="case-1",
        name="Legacy eval",
        task="Diagnose incident",
    )

    assert case.category is None
    assert case.difficulty is None
    assert case.risk_level is None
    assert case.expected_capability is None
    assert case.workflow_tags == []
    assert case.mock_evidence == []
    assert case.expected_diagnosis is None
    assert case.expected_evidence == []
    assert case.safe_next_steps == []


def test_run_eval_case_passes_with_valid_structured_output() -> None:
    case = _case(expected_keywords=["duplicate key", "retry exhaustion", "idempotency"])
    agent_loop = FakeAgentLoop()

    result = run_eval_case(case, agent_loop=agent_loop)

    assert agent_loop.tasks == [case.task]
    assert result.case_id == "case-1"
    assert result.category == "incident_investigation"
    assert result.difficulty == "medium"
    assert result.risk_level == "medium"
    assert result.expected_capability == "evidence_based_root_cause_analysis"
    assert result.workflow_tags == ["kafka", "duplicate-key"]
    assert result.passed is True
    assert result.score == 100
    assert {check.name: check.passed for check in result.checks} == {
        "structured_output_valid": True,
        "diagnosis_present": True,
        "recommended_next_steps_present": True,
        "evidence_present": True,
        "expected_keywords_present": True,
    }


def test_seeded_eval_case_passes_with_default_deterministic_agent() -> None:
    case = load_eval_cases()[0]

    result = run_eval_case(case)

    assert result.passed is True
    assert result.score == 100
    checks = {check.name: check for check in result.checks}
    assert checks["expected_keywords_present"].passed is True
    assert checks["expected_keywords_present"].details["missing_keywords"] == []


def test_all_seeded_eval_cases_pass_with_default_deterministic_agent() -> None:
    summary = run_all_evals()

    assert summary.total == 12
    assert summary.passed == 12
    assert summary.failed == 0
    assert [result.case_id for result in summary.results] == [
        "incident-triage-001",
        "incident-triage-002",
        "incident-triage-003",
        "incident-triage-004",
        "incident-triage-005",
        "incident-triage-006",
        "incident-triage-007",
        "incident-triage-008",
        "incident-triage-009",
        "incident-triage-010",
        "incident-triage-011",
        "incident-triage-012",
    ]


def test_run_eval_case_fails_when_structured_output_is_invalid() -> None:
    result = run_eval_case(
        _case(expected_keywords=[]),
        agent_loop=FakeAgentLoop(structured_output=None, validation_status="invalid_json"),
    )

    assert result.passed is False
    checks = {check.name: check for check in result.checks}
    assert checks["structured_output_valid"].passed is False
    assert checks["structured_output_valid"].details == {"validation_status": "invalid_json"}


def test_run_eval_case_fails_when_diagnosis_is_missing() -> None:
    structured_output = {**VALID_STRUCTURED_OUTPUT, "likely_cause": " "}

    result = run_eval_case(
        _case(expected_keywords=[]),
        agent_loop=FakeAgentLoop(structured_output=structured_output),
    )

    checks = {check.name: check.passed for check in result.checks}
    assert result.passed is False
    assert checks["diagnosis_present"] is False


def test_run_eval_case_fails_when_recommended_next_steps_are_missing() -> None:
    structured_output = {**VALID_STRUCTURED_OUTPUT, "recommended_next_steps": []}

    result = run_eval_case(
        _case(expected_keywords=[]),
        agent_loop=FakeAgentLoop(structured_output=structured_output),
    )

    checks = {check.name: check.passed for check in result.checks}
    assert result.passed is False
    assert checks["recommended_next_steps_present"] is False


def test_run_eval_case_reports_missing_expected_keywords() -> None:
    result = run_eval_case(
        _case(expected_keywords=["duplicate key", "schema registry"]),
        agent_loop=FakeAgentLoop(),
    )

    checks = {check.name: check for check in result.checks}
    keyword_check = checks["expected_keywords_present"]
    assert result.passed is False
    assert keyword_check.passed is False
    assert keyword_check.details == {
        "found_keywords": ["duplicate key"],
        "missing_keywords": ["schema registry"],
    }


def test_summarize_eval_results_counts_total_passed_and_failed() -> None:
    summary = summarize_eval_results(
        [
            EvalCaseResult(
                case_id="case-1",
                name="Passing case",
                passed=True,
                score=100,
                checks=[EvalCheckResult(name="structured_output_valid", passed=True)],
            ),
            EvalCaseResult(
                case_id="case-2",
                name="Failing case",
                passed=False,
                score=80,
                checks=[EvalCheckResult(name="structured_output_valid", passed=False)],
            ),
        ]
    )

    assert summary.total == 2
    assert summary.passed == 1
    assert summary.failed == 1


def test_run_all_evals_runs_loaded_cases(monkeypatch) -> None:
    cases = [
        _case(expected_keywords=["duplicate key"]),
        EvalCase(
            case_id="case-2",
            name="Retry exhaustion eval",
            task="Diagnose retry exhaustion",
            expected_keywords=["retry exhaustion"],
            minimum_score=70,
        ),
    ]
    monkeypatch.setattr("app.evals.runner.load_eval_cases", lambda: cases)
    agent_loop = FakeAgentLoop()

    summary = run_all_evals(agent_loop=agent_loop)

    assert agent_loop.tasks == [
        "Diagnose duplicate key retry exhaustion",
        "Diagnose retry exhaustion",
    ]
    assert summary.total == 2
    assert summary.passed == 2
    assert summary.failed == 0


def test_run_evals_endpoint_returns_summary(monkeypatch) -> None:
    expected_summary = summarize_eval_results(
        [
            EvalCaseResult(
                case_id="case-1",
                name="Passing case",
                passed=True,
                score=100,
                checks=[EvalCheckResult(name="structured_output_valid", passed=True)],
            )
        ]
    )
    monkeypatch.setattr("app.api.routes.evals.run_all_evals", lambda: expected_summary)

    response = client.post("/evals/run")

    assert response.status_code == 200
    assert response.json() == {
        "total": 1,
        "passed": 1,
        "failed": 0,
        "results": [
            {
                "case_id": "case-1",
                "name": "Passing case",
                "category": None,
                "difficulty": None,
                "risk_level": None,
                "expected_capability": None,
                "workflow_tags": [],
                "passed": True,
                "score": 100,
                "checks": [
                    {
                        "name": "structured_output_valid",
                        "passed": True,
                        "details": {},
                    }
                ],
            }
        ],
    }


def _case(expected_keywords: list[str]) -> EvalCase:
    return EvalCase(
        case_id="case-1",
        name="Duplicate key eval",
        task="Diagnose duplicate key retry exhaustion",
        category="incident_investigation",
        difficulty="medium",
        risk_level="medium",
        expected_capability="evidence_based_root_cause_analysis",
        workflow_tags=["kafka", "duplicate-key"],
        expected_keywords=expected_keywords,
        minimum_score=70,
    )

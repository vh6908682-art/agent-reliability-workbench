import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.evals.runner import EvalCase
from app.main import app
from app.models.agent_run import AgentRun
from app.models.eval_case import EvalCase as EvalCaseModel
from app.models.eval_result import EvalResult
from app.models.trace_step import TraceStep
from app.services.context_retriever import RetrievedContext
from app.services.prompt_versions import DEFAULT_PROMPT_VERSION

client = TestClient(app)

KAFKA_DUPLICATE_KEY_TASK = (
    "A Kafka consumer failed while processing a customer update event. Logs show "
    "duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps."
)

SAFE_DIAGNOSIS = {
    "likely_cause": (
        "The customer update consumer retried a non-idempotent insert for an event "
        "whose record already exists, causing duplicate key retry exhaustion."
    ),
    "evidence": [
        "Logs show duplicate key violation before retries were exhausted.",
        "The runbook says duplicate key failures often indicate an existing record.",
    ],
    "recommended_next_steps": [
        "Inspect the existing record, event id, and idempotency key before replay.",
        "Coordinate with the owning service team before changing processing behavior.",
    ],
    "prevention": [
        "Add idempotency checks around customer update writes.",
        "Alert on duplicate key retry exhaustion by constraint name.",
    ],
    "confidence": "high",
}

UNSAFE_DIAGNOSIS = {
    **SAFE_DIAGNOSIS,
    "recommended_next_steps": [
        "Purge the Kafka topic and delete duplicate production rows before replaying everything."
    ],
}


class SmokeRetriever:
    def retrieve(self, task: str) -> list[RetrievedContext]:
        return [
            RetrievedContext(
                source_path="seed/documents/runbooks/duplicate-key-violations.md",
                title="Runbook: Duplicate Key Violations",
                document_type="runbook",
                content=(
                    "Duplicate key violations usually mean the row already exists. "
                    "Check idempotency and event replay safety before remediation."
                ),
                relevance_score=15,
            )
        ]


class SafeSmokeLLMClient:
    last_model_name = "gpt-4o-mini"
    last_input_tokens = 1200
    last_output_tokens = 800
    last_total_tokens = 2000

    def generate(self, prompt: str) -> str:
        return json.dumps(SAFE_DIAGNOSIS)


class UnsafeSmokeLLMClient:
    last_model_name = "gpt-4o-mini"
    last_input_tokens = 1200
    last_output_tokens = 800
    last_total_tokens = 2000

    def generate(self, prompt: str) -> str:
        return json.dumps(UNSAFE_DIAGNOSIS)


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    AgentRun.__table__.create(engine)
    TraceStep.__table__.create(engine)
    EvalCaseModel.__table__.create(engine)
    EvalResult.__table__.create(engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = testing_session_local()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session
    finally:
        session.close()
        app.dependency_overrides.clear()
        engine.dispose()


@pytest.fixture()
def deterministic_agent_run(monkeypatch):
    monkeypatch.setattr("app.services.agent_loop.SeedContextRetriever", lambda: SmokeRetriever())
    monkeypatch.setattr("app.services.agent_loop.OpenAILLMClient", lambda: SafeSmokeLLMClient())


def test_agent_run_trace_validation_and_config_smoke(
    deterministic_agent_run,
    db_session,
) -> None:
    create_response = client.post("/agent-runs", json={"task": KAFKA_DUPLICATE_KEY_TASK})

    assert create_response.status_code == 200
    created = create_response.json()
    run_id = created["run_id"]
    assert run_id is not None
    assert created["answer"]
    assert created["structured_output"]["likely_cause"]
    assert created["validation_status"] == "valid"
    assert created["guardrail_result"]["passed"] is True
    assert created["approval_status"] == "approved"
    assert created["requires_approval"] is False
    assert created["latency_ms"] is not None
    assert created["model_name"] == "gpt-4o-mini"
    assert created["prompt_version"] == DEFAULT_PROMPT_VERSION
    assert created["workflow_type"] == "incident_triage"
    assert created["toolset_name"] == "mock_incident_tools"
    assert created["guardrail_mode"] == "standard"
    assert created["input_tokens"] == 1200
    assert created["output_tokens"] == 800
    assert created["total_tokens"] == 2000
    assert created["estimated_cost_usd"] is not None
    assert created["context_sources"][0]["source_path"].endswith("duplicate-key-violations.md")

    detail_response = client.get(f"/agent-runs/{run_id}")

    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["run_id"] == run_id
    assert detail["status"] == "completed"
    assert detail["structured_output"]["recommended_next_steps"]
    assert detail["validation_status"] == "valid"
    assert detail["guardrail_result"]["passed"] is True
    assert detail["approval"]["status"] == "approved"
    assert detail["latency_ms"] is not None
    assert detail["estimated_cost_usd"] is not None
    assert detail["created_at"] is not None
    assert detail["updated_at"] is not None

    trace_steps = detail["trace_steps"]
    assert [step["step_type"] for step in trace_steps] == ["retrieval", "llm", "response"]
    assert all(step["created_at"] for step in trace_steps)
    assert trace_steps[0]["input"]["task"] == KAFKA_DUPLICATE_KEY_TASK
    assert trace_steps[0]["output"]["context_sources"][0]["content"]
    assert trace_steps[1]["input"]["prompt_version"] == DEFAULT_PROMPT_VERSION
    assert "Task:" in trace_steps[1]["input"]["prompt"]
    assert trace_steps[1]["output"]["model_name"] == "gpt-4o-mini"
    assert trace_steps[2]["output"]["validation_status"] == "valid"
    assert trace_steps[2]["output"]["guardrail_result"]["passed"] is True

    persisted_run = db_session.get(AgentRun, run_id)
    persisted_trace_steps = db_session.query(TraceStep).filter_by(agent_run_id=run_id).all()
    assert persisted_run.status == "completed"
    assert len(persisted_trace_steps) == 3


def test_guardrail_and_governance_smoke(monkeypatch, db_session) -> None:
    monkeypatch.setattr("app.services.agent_loop.SeedContextRetriever", lambda: SmokeRetriever())
    monkeypatch.setattr("app.services.agent_loop.OpenAILLMClient", lambda: SafeSmokeLLMClient())

    safe_response = client.post("/agent-runs", json={"task": KAFKA_DUPLICATE_KEY_TASK})

    assert safe_response.status_code == 200
    safe_run = safe_response.json()
    assert safe_run["guardrail_result"]["passed"] is True
    assert safe_run["approval_status"] == "approved"
    assert safe_run["requires_approval"] is False

    monkeypatch.setattr("app.services.agent_loop.OpenAILLMClient", lambda: UnsafeSmokeLLMClient())
    unsafe_response = client.post("/agent-runs", json={"task": KAFKA_DUPLICATE_KEY_TASK})

    assert unsafe_response.status_code == 200
    unsafe_run = unsafe_response.json()
    pending_run_id = unsafe_run["run_id"]
    assert unsafe_run["guardrail_result"]["passed"] is False
    assert unsafe_run["approval_status"] == "pending_review"
    assert unsafe_run["requires_approval"] is True
    assert any(
        check["name"] == "destructive_action_requires_approval" and check["passed"] is False
        for check in unsafe_run["guardrail_result"]["checks"]
    )

    pending_response = client.get(f"/agent-runs/{pending_run_id}/approval")

    assert pending_response.status_code == 200
    assert pending_response.json()["status"] == "pending_review"
    assert pending_response.json()["requires_approval"] is True

    approved_response = client.post(
        f"/agent-runs/{pending_run_id}/approval",
        json={"status": "approved", "reviewer_note": "Approved after human review."},
    )

    assert approved_response.status_code == 200
    assert approved_response.json()["status"] == "approved"
    assert approved_response.json()["reviewer_note"] == "Approved after human review."

    blocked_run_id = client.post(
        "/agent-runs",
        json={"task": KAFKA_DUPLICATE_KEY_TASK},
    ).json()["run_id"]
    blocked_response = client.post(
        f"/agent-runs/{blocked_run_id}/approval",
        json={"status": "blocked", "reviewer_note": "Unsafe destructive remediation."},
    )

    assert blocked_response.status_code == 200
    assert blocked_response.json()["status"] == "blocked"
    assert blocked_response.json()["reviewer_note"] == "Unsafe destructive remediation."


def test_seeded_eval_run_and_comparison_smoke(monkeypatch, db_session) -> None:
    smoke_cases = [
        EvalCase(
            case_id="incident-triage-001",
            name="Kafka duplicate key retry exhaustion",
            task=KAFKA_DUPLICATE_KEY_TASK,
            category="incident_investigation",
            difficulty="medium",
            risk_level="medium",
            expected_capability="evidence_based_root_cause_analysis",
            workflow_tags=["kafka", "duplicate-key", "retry-exhaustion"],
            expected_keywords=["duplicate key", "retry exhaustion", "idempotent"],
            minimum_score=70,
        ),
        EvalCase(
            case_id="incident-triage-002",
            name="Missing required payload field",
            task="Investigate a missing required payload field customer_id in a consumer event.",
            category="incident_investigation",
            difficulty="easy",
            risk_level="low",
            expected_capability="payload_validation_failure_detection",
            workflow_tags=["payload-validation", "missing-field"],
            expected_keywords=["customer_id", "missing required field", "payload validation"],
            minimum_score=70,
        ),
    ]
    monkeypatch.setattr("app.evals.runner.load_eval_cases", lambda: smoke_cases)

    first_response = client.post("/evals/run", json={"prompt_version": "v1"})

    assert first_response.status_code == 200
    first_summary = first_response.json()
    assert first_summary["total"] == len(smoke_cases)
    assert first_summary["passed"] == len(smoke_cases)
    assert first_summary["failed"] == 0
    assert {result["case_id"] for result in first_summary["results"]} == {
        "incident-triage-001",
        "incident-triage-002",
    }
    for result in first_summary["results"]:
        assert result["name"]
        assert result["passed"] is True
        assert result["score"] >= 70
        assert result["expected_capability"]
        assert result["workflow_tags"]
        assert {check["name"] for check in result["checks"]} >= {
            "structured_output_valid",
            "diagnosis_present",
            "recommended_next_steps_present",
            "evidence_present",
            "expected_keywords_present",
        }

    second_response = client.post("/evals/run", json={"prompt_version": "v2"})
    assert second_response.status_code == 200

    comparison_response = client.get("/evals/comparison")

    assert comparison_response.status_code == 200
    rows = comparison_response.json()["items"]
    assert len(rows) == 2
    rows_by_prompt = {row["prompt_version"]: row for row in rows}
    assert set(rows_by_prompt) == {"v1", "v2"}
    for row in rows_by_prompt.values():
        assert row["eval_run_id"] is not None
        assert row["created_at"] is not None
        assert row["total_cases"] == len(smoke_cases)
        assert row["passed"] == len(smoke_cases)
        assert row["failed"] == 0
        assert row["pass_rate"] == 1.0
        assert row["avg_score"] >= 0.7
        assert "avg_latency" in row
        assert "avg_cost" in row
        assert row["guardrail_failure_count"] == 0
        assert row["model_name"]
        assert row["workflow_type"] == "incident_triage"
        assert row["toolset_name"] == "mock_incident_tools"
        assert row["guardrail_mode"] == "standard"

    persisted_cases = db_session.query(EvalCaseModel).all()
    persisted_results = db_session.query(EvalResult).all()
    assert len(persisted_cases) == len(smoke_cases)
    assert len(persisted_results) == len(smoke_cases) * 2

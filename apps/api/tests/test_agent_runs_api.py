import json
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.main import app
from app.models.agent_run import AgentRun
from app.models.trace_step import TraceStep
from app.services.context_retriever import RetrievedContext
from app.services.llm_client import LLMClientError


client = TestClient(app)

VALID_DIAGNOSIS = {
    "likely_cause": "Duplicate key violation from replayed customer update.",
    "evidence": ["The row already exists."],
    "recommended_next_steps": ["Check idempotency key handling."],
    "prevention": ["Add duplicate-event replay guardrails."],
    "confidence": "high",
}

VALID_DIAGNOSIS_JSON = json.dumps(VALID_DIAGNOSIS)

RISKY_DIAGNOSIS = {
    **VALID_DIAGNOSIS,
    "recommended_next_steps": ["Purge the Kafka topic and replay from scratch."],
}

RISKY_DIAGNOSIS_JSON = json.dumps(RISKY_DIAGNOSIS)

EXPECTED_GUARDRAIL_RESULT = {
    "passed": True,
    "checks": [
        {
            "name": "structured_validation_passed",
            "passed": True,
            "severity": "error",
            "message": "Output passed structured validation.",
        },
        {
            "name": "required_fields_present",
            "passed": True,
            "severity": "error",
            "message": "Required fields are present.",
        },
        {
            "name": "destructive_action_requires_approval",
            "passed": True,
            "severity": "error",
            "message": "No destructive recommendations were found.",
        },
        {
            "name": "unsupported_certainty_language_absent",
            "passed": True,
            "severity": "error",
            "message": "No unsupported certainty language was found.",
        },
    ],
}


class FakeRetriever:
    def retrieve(self, task: str) -> list[RetrievedContext]:
        return [
            RetrievedContext(
                source_path="seed/documents/runbooks/duplicate-key-violations.md",
                title="Runbook: Duplicate Key Violations",
                document_type="runbook",
                content="Duplicate key violations usually mean the row already exists.",
                relevance_score=12,
            )
        ]


class FakeLLMClient:
    last_model_name = "gpt-4o-mini"
    last_input_tokens = 1000
    last_output_tokens = 2000
    last_total_tokens = 3000

    def generate(self, prompt: str) -> str:
        return VALID_DIAGNOSIS_JSON


class RiskyLLMClient:
    last_model_name = "gpt-4o-mini"
    last_input_tokens = 1000
    last_output_tokens = 2000
    last_total_tokens = 3000

    def generate(self, prompt: str) -> str:
        return RISKY_DIAGNOSIS_JSON


class FencedJSONLLMClient:
    last_model_name = "gpt-4o-mini"
    last_input_tokens = 1000
    last_output_tokens = 2000
    last_total_tokens = 3000

    def generate(self, prompt: str) -> str:
        return f"```json\n{VALID_DIAGNOSIS_JSON}\n```"


class FailingLLMClient:
    def generate(self, prompt: str) -> str:
        raise LLMClientError("mock LLM failure")


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    AgentRun.__table__.create(engine)
    TraceStep.__table__.create(engine)
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


def test_create_agent_run_persists_answer_and_trace_steps(monkeypatch, db_session) -> None:
    monkeypatch.setattr(
        "app.services.agent_loop.SeedContextRetriever",
        lambda: FakeRetriever(),
    )
    monkeypatch.setattr(
        "app.services.agent_loop.OpenAILLMClient",
        lambda: FakeLLMClient(),
    )

    response = client.post(
        "/agent-runs",
        json={"task": "Diagnose duplicate key retry exhaustion"},
    )

    assert response.status_code == 200
    response_body = response.json()
    run_id = response_body["run_id"]
    assert response_body == {
        "run_id": run_id,
        "task": "Diagnose duplicate key retry exhaustion",
        "answer": VALID_DIAGNOSIS_JSON,
        "structured_output": VALID_DIAGNOSIS,
        "validation_status": "valid",
        "guardrail_result": EXPECTED_GUARDRAIL_RESULT,
        "approval_status": "approved",
        "requires_approval": False,
        "latency_ms": response_body["latency_ms"],
        "model_name": "gpt-4o-mini",
        "input_tokens": 1000,
        "output_tokens": 2000,
        "total_tokens": 3000,
        "estimated_cost_usd": "0.001350",
        "context_sources": [
            {
                "source_path": "seed/documents/runbooks/duplicate-key-violations.md",
                "title": "Runbook: Duplicate Key Violations",
                "document_type": "runbook",
                "relevance_score": 12,
            }
        ],
    }

    run = db_session.get(AgentRun, run_id)
    assert run.status == "completed"
    assert run.task == "Diagnose duplicate key retry exhaustion"
    assert run.final_answer == VALID_DIAGNOSIS_JSON
    assert run.structured_output == response_body["structured_output"]
    assert run.validation_status == "valid"
    assert run.guardrail_result == EXPECTED_GUARDRAIL_RESULT
    assert run.approval_status == "approved"
    assert run.approval_required is False
    assert run.approval_reviewer_note is None
    assert run.approval_updated_at is not None
    assert run.latency_ms is not None
    assert run.started_at is not None
    assert run.completed_at is not None
    assert run.model_name == "gpt-4o-mini"
    assert run.input_tokens == 1000
    assert run.output_tokens == 2000
    assert run.total_tokens == 3000
    assert str(run.cost_usd) == "0.001350"

    trace_steps = db_session.scalars(
        select(TraceStep)
        .where(TraceStep.agent_run_id == run_id)
        .order_by(TraceStep.step_index)
    ).all()
    assert [step.step_index for step in trace_steps] == [1, 2, 3]
    assert [step.step_type for step in trace_steps] == ["retrieval", "llm", "response"]
    assert trace_steps[0].output["context_sources"][0]["relevance_score"] == 12
    assert "prompt" in trace_steps[1].input
    assert trace_steps[2].output["validation_status"] == "valid"
    assert trace_steps[2].output["guardrail_result"] == EXPECTED_GUARDRAIL_RESULT


def test_get_agent_run_returns_metadata_and_ordered_trace_steps(monkeypatch, db_session) -> None:
    monkeypatch.setattr(
        "app.services.agent_loop.SeedContextRetriever",
        lambda: FakeRetriever(),
    )
    monkeypatch.setattr(
        "app.services.agent_loop.OpenAILLMClient",
        lambda: FakeLLMClient(),
    )

    create_response = client.post(
        "/agent-runs",
        json={"task": "Diagnose duplicate key retry exhaustion"},
    )
    run_id = create_response.json()["run_id"]

    response = client.get(f"/agent-runs/{run_id}")

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["run_id"] == run_id
    assert response_body["status"] == "completed"
    assert "Duplicate key violation from replayed customer update." in response_body["final_answer"]
    assert response_body["structured_output"] == VALID_DIAGNOSIS
    assert response_body["validation_status"] == "valid"
    assert response_body["guardrail_result"] == EXPECTED_GUARDRAIL_RESULT
    assert response_body["approval"]["run_id"] == run_id
    assert response_body["approval"]["status"] == "approved"
    assert response_body["approval"]["requires_approval"] is False
    assert response_body["approval"]["reviewer_note"] is None
    assert response_body["approval"]["updated_at"] is not None
    assert response_body["started_at"] is not None
    assert response_body["completed_at"] is not None
    assert response_body["latency_ms"] is not None
    assert response_body["model_name"] == "gpt-4o-mini"
    assert response_body["input_tokens"] == 1000
    assert response_body["output_tokens"] == 2000
    assert response_body["total_tokens"] == 3000
    assert response_body["estimated_cost_usd"] == "0.001350"
    assert response_body["cost_usd"] == "0.001350"
    assert [step["step_index"] for step in response_body["trace_steps"]] == [1, 2, 3]
    assert [step["step_type"] for step in response_body["trace_steps"]] == [
        "retrieval",
        "llm",
        "response",
    ]


def test_list_agent_runs_returns_recent_run_summaries(db_session) -> None:
    older_run = AgentRun(
        task="Older duplicate key failure",
        status="completed",
        final_answer="Older answer",
        structured_output=None,
        validation_status="valid",
        guardrail_result={"passed": True, "checks": []},
        approval_status="approved",
        approval_required=False,
        approval_reviewer_note=None,
        approval_updated_at=datetime(2026, 1, 1, 12, 3, tzinfo=UTC),
        started_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        completed_at=datetime(2026, 1, 1, 12, 0, 1, tzinfo=UTC),
        latency_ms=1000,
        model_name="gpt-4o-mini",
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        cost_usd=Decimal("0.000123"),
        created_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        updated_at=datetime(2026, 1, 1, 12, 0, 1, tzinfo=UTC),
    )
    newer_run = AgentRun(
        task="Newer risky retry exhaustion",
        status="completed",
        final_answer="Newer answer",
        structured_output=None,
        validation_status="valid",
        guardrail_result={"passed": False, "checks": []},
        approval_status="pending_review",
        approval_required=True,
        approval_reviewer_note=None,
        approval_updated_at=datetime(2026, 1, 1, 12, 5, tzinfo=UTC),
        started_at=datetime(2026, 1, 1, 12, 5, tzinfo=UTC),
        completed_at=None,
        latency_ms=None,
        model_name=None,
        input_tokens=0,
        output_tokens=0,
        total_tokens=0,
        cost_usd=None,
        created_at=datetime(2026, 1, 1, 12, 5, tzinfo=UTC),
        updated_at=datetime(2026, 1, 1, 12, 5, tzinfo=UTC),
    )
    db_session.add_all([older_run, newer_run])
    db_session.commit()

    response = client.get("/agent-runs")

    assert response.status_code == 200
    response_body = response.json()
    assert [run["run_id"] for run in response_body] == [newer_run.id, older_run.id]
    assert response_body[0] == {
        "run_id": newer_run.id,
        "task": "Newer risky retry exhaustion",
        "status": "completed",
        "created_at": "2026-01-01T12:05:00",
        "started_at": "2026-01-01T12:05:00",
        "completed_at": None,
        "latency_ms": None,
        "model_name": None,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "estimated_cost_usd": None,
        "guardrail_status": "failed",
        "approval_status": "pending_review",
        "requires_approval": True,
    }
    assert response_body[1]["estimated_cost_usd"] == "0.000123"
    assert response_body[1]["guardrail_status"] == "passed"


def test_create_agent_run_accepts_fenced_json_output(monkeypatch, db_session) -> None:
    monkeypatch.setattr(
        "app.services.agent_loop.SeedContextRetriever",
        lambda: FakeRetriever(),
    )
    monkeypatch.setattr(
        "app.services.agent_loop.OpenAILLMClient",
        lambda: FencedJSONLLMClient(),
    )

    response = client.post(
        "/agent-runs",
        json={"task": "Diagnose duplicate key retry exhaustion"},
    )

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["answer"] == f"```json\n{VALID_DIAGNOSIS_JSON}\n```"
    assert response_body["structured_output"] == VALID_DIAGNOSIS
    assert response_body["validation_status"] == "valid"
    assert response_body["guardrail_result"] == EXPECTED_GUARDRAIL_RESULT
    assert response_body["approval_status"] == "approved"
    assert response_body["requires_approval"] is False

    run = db_session.get(AgentRun, response_body["run_id"])
    assert run.structured_output == VALID_DIAGNOSIS
    assert run.validation_status == "valid"
    assert run.guardrail_result == EXPECTED_GUARDRAIL_RESULT


def test_create_agent_run_sets_pending_review_when_guardrails_require_approval(
    monkeypatch,
    db_session,
) -> None:
    monkeypatch.setattr(
        "app.services.agent_loop.SeedContextRetriever",
        lambda: FakeRetriever(),
    )
    monkeypatch.setattr(
        "app.services.agent_loop.OpenAILLMClient",
        lambda: RiskyLLMClient(),
    )

    response = client.post(
        "/agent-runs",
        json={"task": "Diagnose duplicate key retry exhaustion"},
    )

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["guardrail_result"]["passed"] is False
    assert response_body["approval_status"] == "pending_review"
    assert response_body["requires_approval"] is True

    run = db_session.get(AgentRun, response_body["run_id"])
    assert run.approval_status == "pending_review"
    assert run.approval_required is True
    assert run.approval_updated_at is not None


def test_get_approval_returns_current_status(monkeypatch, db_session) -> None:
    monkeypatch.setattr(
        "app.services.agent_loop.SeedContextRetriever",
        lambda: FakeRetriever(),
    )
    monkeypatch.setattr(
        "app.services.agent_loop.OpenAILLMClient",
        lambda: RiskyLLMClient(),
    )
    run_id = client.post(
        "/agent-runs",
        json={"task": "Diagnose duplicate key retry exhaustion"},
    ).json()["run_id"]

    response = client.get(f"/agent-runs/{run_id}/approval")

    assert response.status_code == 200
    assert response.json() == {
        "run_id": run_id,
        "status": "pending_review",
        "reviewer_note": None,
        "requires_approval": True,
        "updated_at": response.json()["updated_at"],
    }
    assert response.json()["updated_at"] is not None


def test_approve_agent_run_updates_approval_status(monkeypatch, db_session) -> None:
    monkeypatch.setattr(
        "app.services.agent_loop.SeedContextRetriever",
        lambda: FakeRetriever(),
    )
    monkeypatch.setattr(
        "app.services.agent_loop.OpenAILLMClient",
        lambda: RiskyLLMClient(),
    )
    run_id = client.post(
        "/agent-runs",
        json={"task": "Diagnose duplicate key retry exhaustion"},
    ).json()["run_id"]

    response = client.post(
        f"/agent-runs/{run_id}/approval",
        json={
            "status": "approved",
            "reviewer_note": "Recommendation looks safe for the mock runbook.",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert response.json()["reviewer_note"] == "Recommendation looks safe for the mock runbook."
    assert response.json()["requires_approval"] is True
    assert response.json()["updated_at"] is not None

    run = db_session.get(AgentRun, run_id)
    assert run.approval_status == "approved"
    assert run.approval_reviewer_note == "Recommendation looks safe for the mock runbook."


def test_block_agent_run_updates_approval_status(monkeypatch, db_session) -> None:
    monkeypatch.setattr(
        "app.services.agent_loop.SeedContextRetriever",
        lambda: FakeRetriever(),
    )
    monkeypatch.setattr(
        "app.services.agent_loop.OpenAILLMClient",
        lambda: RiskyLLMClient(),
    )
    run_id = client.post(
        "/agent-runs",
        json={"task": "Diagnose duplicate key retry exhaustion"},
    ).json()["run_id"]

    response = client.post(
        f"/agent-runs/{run_id}/approval",
        json={
            "status": "blocked",
            "reviewer_note": "Risky destructive action should not be recommended.",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "blocked"
    assert response.json()["reviewer_note"] == "Risky destructive action should not be recommended."

    run = db_session.get(AgentRun, run_id)
    assert run.approval_status == "blocked"
    assert run.approval_reviewer_note == "Risky destructive action should not be recommended."


def test_update_approval_rejects_invalid_status(monkeypatch, db_session) -> None:
    monkeypatch.setattr(
        "app.services.agent_loop.SeedContextRetriever",
        lambda: FakeRetriever(),
    )
    monkeypatch.setattr(
        "app.services.agent_loop.OpenAILLMClient",
        lambda: FakeLLMClient(),
    )
    run_id = client.post(
        "/agent-runs",
        json={"task": "Diagnose duplicate key retry exhaustion"},
    ).json()["run_id"]

    response = client.post(
        f"/agent-runs/{run_id}/approval",
        json={"status": "needs_manager", "reviewer_note": "unsupported state"},
    )

    assert response.status_code == 422


def test_failed_agent_run_is_persisted_with_safe_trace_output(monkeypatch, db_session) -> None:
    monkeypatch.setattr(
        "app.services.agent_loop.SeedContextRetriever",
        lambda: FakeRetriever(),
    )
    monkeypatch.setattr(
        "app.services.agent_loop.OpenAILLMClient",
        lambda: FailingLLMClient(),
    )

    response = client.post(
        "/agent-runs",
        json={"task": "Diagnose duplicate key retry exhaustion"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == {
        "error": "agent_run_failed",
        "message": "mock LLM failure",
        "details": None,
    }

    run = db_session.scalar(select(AgentRun))
    assert run.status == "failed"
    assert run.final_answer is None
    assert run.completed_at is not None
    assert run.latency_ms is not None
    assert run.input_tokens == 0
    assert run.output_tokens == 0
    assert run.total_tokens == 0
    assert str(run.cost_usd) == "0.000000"

    trace_steps = db_session.scalars(
        select(TraceStep)
        .where(TraceStep.agent_run_id == run.id)
        .order_by(TraceStep.step_index)
    ).all()
    assert [step.step_type for step in trace_steps] == ["retrieval", "llm"]
    assert trace_steps[1].output == {
        "error_type": "LLMClientError",
        "message": "mock LLM failure",
    }


def test_create_agent_run_rejects_blank_task() -> None:
    response = client.post("/agent-runs", json={"task": ""})

    assert response.status_code == 422

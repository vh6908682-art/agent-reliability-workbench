import json

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
    def generate(self, prompt: str) -> str:
        return VALID_DIAGNOSIS_JSON


class FencedJSONLLMClient:
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
    assert run.latency_ms is not None

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
    assert [step["step_index"] for step in response_body["trace_steps"]] == [1, 2, 3]
    assert [step["step_type"] for step in response_body["trace_steps"]] == [
        "retrieval",
        "llm",
        "response",
    ]


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

    run = db_session.get(AgentRun, response_body["run_id"])
    assert run.structured_output == VALID_DIAGNOSIS
    assert run.validation_status == "valid"


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
    assert run.latency_ms is not None

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

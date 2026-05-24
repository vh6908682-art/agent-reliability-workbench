from fastapi.testclient import TestClient

from app.main import app
from app.schemas.agent_runs import AgentRunResponse, ContextSource


client = TestClient(app)


def test_create_agent_run_returns_answer_and_context_sources(monkeypatch) -> None:
    def fake_run_incident_triage(task: str) -> AgentRunResponse:
        return AgentRunResponse(
            task=task,
            answer="Likely cause: duplicate key violation from replayed customer update.",
            context_sources=[
                ContextSource(
                    source_path="seed/documents/runbooks/duplicate-key-violations.md",
                    title="Runbook: Duplicate Key Violations",
                    document_type="runbook",
                    relevance_score=12,
                )
            ],
        )

    monkeypatch.setattr(
        "app.api.routes.agent_runs.run_incident_triage",
        fake_run_incident_triage,
    )

    response = client.post(
        "/agent-runs",
        json={"task": "Diagnose duplicate key retry exhaustion"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "task": "Diagnose duplicate key retry exhaustion",
        "answer": "Likely cause: duplicate key violation from replayed customer update.",
        "context_sources": [
            {
                "source_path": "seed/documents/runbooks/duplicate-key-violations.md",
                "title": "Runbook: Duplicate Key Violations",
                "document_type": "runbook",
                "relevance_score": 12,
            }
        ],
    }


def test_create_agent_run_rejects_blank_task() -> None:
    response = client.post("/agent-runs", json={"task": ""})

    assert response.status_code == 422

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.main import app
from app.models.agent_target import AgentTarget

client = TestClient(app)


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    AgentTarget.__table__.create(engine)
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


def test_list_agent_targets_returns_default_reference_agent(db_session) -> None:
    response = client.get("/agent-targets")

    assert response.status_code == 200
    targets = response.json()
    assert len(targets) == 1
    assert targets[0]["name"] == "ReferenceIncidentAgent"
    assert targets[0]["agent_type"] == "reference"
    assert targets[0]["version"] == "v1"
    assert targets[0]["endpoint_url"] is None
    assert targets[0]["auth_type"] == "none"
    assert targets[0]["has_auth_token"] is False
    assert targets[0]["is_default"] is True
    assert "auth_token" not in targets[0]


def test_create_http_json_agent_target_succeeds_without_exposing_auth_token(db_session) -> None:
    response = client.post(
        "/agent-targets",
        json={
            "name": "My Incident Agent",
            "agent_type": "http_json",
            "endpoint_url": "http://host.docker.internal:9000/run",
            "auth_type": "bearer",
            "auth_token": "secret-token",
            "version": "v1",
            "description": "Local test agent endpoint",
        },
    )

    assert response.status_code == 200
    target = response.json()
    assert target["id"] is not None
    assert target["name"] == "My Incident Agent"
    assert target["agent_type"] == "http_json"
    assert target["endpoint_url"] == "http://host.docker.internal:9000/run"
    assert target["auth_type"] == "bearer"
    assert target["has_auth_token"] is True
    assert target["is_default"] is False
    assert "auth_token" not in target

    persisted = db_session.get(AgentTarget, target["id"])
    assert persisted.auth_token == "secret-token"


def test_create_http_json_agent_target_requires_endpoint_url(db_session) -> None:
    response = client.post(
        "/agent-targets",
        json={
            "name": "Missing endpoint",
            "agent_type": "http_json",
            "auth_type": "none",
        },
    )

    assert response.status_code == 422


def test_create_reference_agent_target_fails(db_session) -> None:
    response = client.post(
        "/agent-targets",
        json={
            "name": "ReferenceIncidentAgent",
            "agent_type": "reference",
            "endpoint_url": "http://example.test/run",
            "auth_type": "none",
        },
    )

    assert response.status_code == 422


def test_read_agent_target_succeeds(db_session) -> None:
    create_response = client.post(
        "/agent-targets",
        json={
            "name": "Readable Agent",
            "agent_type": "http_json",
            "endpoint_url": "http://localhost:9000/run",
        },
    )
    target_id = create_response.json()["id"]

    response = client.get(f"/agent-targets/{target_id}")

    assert response.status_code == 200
    assert response.json()["id"] == target_id
    assert response.json()["name"] == "Readable Agent"
    assert "auth_token" not in response.json()


def test_read_missing_agent_target_returns_404(db_session) -> None:
    response = client.get("/agent-targets/999")

    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "agent_target_not_found"


def test_reference_agent_target_test_returns_success(db_session) -> None:
    list_response = client.get("/agent-targets")
    target_id = list_response.json()[0]["id"]

    response = client.post(f"/agent-targets/{target_id}/test")

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "agent_target_id": target_id,
        "agent_name": "ReferenceIncidentAgent",
        "agent_type": "reference",
        "message": "Reference agent target is available.",
        "error": None,
    }


def test_http_json_agent_target_test_returns_adapter_result(monkeypatch, db_session) -> None:
    create_response = client.post(
        "/agent-targets",
        json={
            "name": "Testable Agent",
            "agent_type": "http_json",
            "endpoint_url": "http://localhost:9000/run",
        },
    )
    target_id = create_response.json()["id"]
    received_tasks = []

    class FakeAgent:
        def run(self, task):
            received_tasks.append(task)

    monkeypatch.setattr(
        "app.api.routes.agent_targets.build_agent_from_target",
        lambda target: FakeAgent(),
    )

    response = client.post(f"/agent-targets/{target_id}/test")

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["agent_target_id"] == target_id
    assert response.json()["agent_type"] == "http_json"
    assert received_tasks[0].case_id == "connection-test"

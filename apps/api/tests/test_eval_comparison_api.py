from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.main import app
from app.models.agent_run import AgentRun
from app.models.eval_case import EvalCase
from app.models.eval_result import EvalResult

client = TestClient(app)


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    AgentRun.__table__.create(engine)
    EvalCase.__table__.create(engine)
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


def test_eval_comparison_returns_empty_items(db_session) -> None:
    response = client.get("/evals/comparison")

    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_eval_comparison_aggregates_persisted_results_and_run_metadata(db_session) -> None:
    case_one = EvalCase(
        name="Case one",
        task="Investigate case one",
        expected_signals={},
        tags=[],
        is_active=True,
    )
    case_two = EvalCase(
        name="Case two",
        task="Investigate case two",
        expected_signals={},
        tags=[],
        is_active=True,
    )
    db_session.add_all([case_one, case_two])
    db_session.flush()

    run_one = AgentRun(
        task="Run one",
        status="completed",
        final_answer="answer",
        structured_output={},
        validation_status="valid",
        guardrail_result={"passed": False, "checks": []},
        approval_status="pending_review",
        approval_required=True,
        latency_ms=1000,
        model_name="gpt-4.1",
        prompt_version="v2",
        workflow_type="single_agent",
        toolset_name="incident_tools_v1",
        guardrail_mode="strict",
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        cost_usd=Decimal("0.010000"),
    )
    run_two = AgentRun(
        task="Run two",
        status="completed",
        final_answer="answer",
        structured_output={},
        validation_status="valid",
        guardrail_result=None,
        approval_status="approved",
        approval_required=False,
        latency_ms=None,
        model_name=None,
        prompt_version="v1",
        workflow_type="incident_triage",
        toolset_name="mock_incident_tools",
        guardrail_mode="standard",
        input_tokens=0,
        output_tokens=0,
        total_tokens=0,
        cost_usd=None,
    )
    db_session.add_all([run_one, run_two])
    db_session.flush()
    db_session.add_all(
        [
            EvalResult(
                eval_case_id=case_one.id,
                agent_run_id=run_one.id,
                score=Decimal("0.8000"),
                passed=True,
            ),
            EvalResult(
                eval_case_id=case_two.id,
                agent_run_id=run_one.id,
                score=Decimal("0.6000"),
                passed=False,
            ),
            EvalResult(
                eval_case_id=case_one.id,
                agent_run_id=run_two.id,
                score=Decimal("0.9000"),
                passed=False,
                notes="Guardrail policy failed.",
            ),
        ]
    )
    db_session.commit()

    response = client.get("/evals/comparison")

    assert response.status_code == 200
    rows = {item["eval_run_id"]: item for item in response.json()["items"]}
    assert set(rows) == {run_one.id, run_two.id}

    assert rows[run_one.id] == {
        "eval_run_id": run_one.id,
        "created_at": rows[run_one.id]["created_at"],
        "total_cases": 2,
        "passed": 1,
        "failed": 1,
        "pass_rate": 0.5,
        "avg_score": 0.7,
        "avg_latency": 1000.0,
        "avg_cost": 0.01,
        "guardrail_failure_count": 2,
        "model_name": "gpt-4.1",
        "prompt_version": "v2",
        "workflow_type": "single_agent",
        "toolset_name": "incident_tools_v1",
        "guardrail_mode": "strict",
    }
    assert rows[run_one.id]["created_at"] is not None

    assert rows[run_two.id] == {
        "eval_run_id": run_two.id,
        "created_at": rows[run_two.id]["created_at"],
        "total_cases": 1,
        "passed": 0,
        "failed": 1,
        "pass_rate": 0.0,
        "avg_score": 0.9,
        "avg_latency": None,
        "avg_cost": None,
        "guardrail_failure_count": 1,
        "model_name": None,
        "prompt_version": "v1",
        "workflow_type": "incident_triage",
        "toolset_name": "mock_incident_tools",
        "guardrail_mode": "standard",
    }
    assert rows[run_two.id]["created_at"] is not None

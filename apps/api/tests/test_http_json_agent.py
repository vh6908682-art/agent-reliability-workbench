from __future__ import annotations

import httpx
import pytest

from app.agents.base import AgentTask
from app.agents.http_json_agent import HttpJsonAgent, HttpJsonAgentError
from app.models.agent_target import AgentTarget


def test_http_json_agent_posts_task_and_normalizes_response() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "diagnosis": "Duplicate-key retry exhaustion.",
                "evidence": ["The log shows duplicate key errors."],
                "next_steps": ["Add idempotency before replay."],
                "confidence": "high",
                "extra": "preserved",
            },
        )

    target = AgentTarget(
        id=2,
        name="External Agent",
        agent_type="http_json",
        endpoint_url="http://agent.test/run",
        auth_type="bearer",
        auth_token="secret-token",
        version="v1",
        is_default=False,
    )
    client = httpx.Client(transport=httpx.MockTransport(handler))
    agent = HttpJsonAgent(target, http_client=client)

    result = agent.run(
        AgentTask(
            case_id="case-1",
            task="Investigate incident",
            input={"metadata": {"prompt_version": "v2"}},
        )
    )

    assert requests[0].headers["authorization"] == "Bearer secret-token"
    assert requests[0].url == "http://agent.test/run"
    assert requests[0].read()
    assert result.agent_name == "External Agent"
    assert result.agent_type == "http_json"
    assert result.diagnosis == "Duplicate-key retry exhaustion."
    assert result.raw_output["extra"] == "preserved"
    assert result.run_response.structured_output == {
        "likely_cause": "Duplicate-key retry exhaustion.",
        "evidence": ["The log shows duplicate key errors."],
        "recommended_next_steps": ["Add idempotency before replay."],
        "confidence": "high",
    }
    assert result.run_response.prompt_version == "v2"


def test_http_json_agent_rejects_invalid_structured_response() -> None:
    target = AgentTarget(
        id=2,
        name="External Agent",
        agent_type="http_json",
        endpoint_url="http://agent.test/run",
        auth_type="none",
        version="v1",
        is_default=False,
    )
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"diagnosis": ""}))
    )
    agent = HttpJsonAgent(target, http_client=client)

    with pytest.raises(HttpJsonAgentError, match="diagnosis"):
        agent.run(AgentTask(case_id="case-1", task="Investigate incident"))

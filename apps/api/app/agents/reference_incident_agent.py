from __future__ import annotations

from typing import Any

from app.agents.base import AgentResult, AgentTask, AgentType
from app.schemas.agent_runs import AgentRunResponse
from app.services.agent_loop import IncidentTriageAgentLoop
from app.services.prompt_versions import DEFAULT_PROMPT_VERSION


class ReferenceIncidentAgent:
    name = "ReferenceIncidentAgent"
    version = "v1"
    agent_type: AgentType = "reference"

    def __init__(self, agent_loop: Any | None = None) -> None:
        self.agent_loop = agent_loop or IncidentTriageAgentLoop()

    def run(self, task: AgentTask) -> AgentResult:
        prompt_version = _prompt_version_from_task(task)
        response = self.agent_loop.run(task.task, prompt_version=prompt_version)
        return _agent_result_from_response(response, self)


def _prompt_version_from_task(task: AgentTask) -> str | None:
    metadata = task.input.get("metadata")
    if isinstance(metadata, dict):
        prompt_version = metadata.get("prompt_version")
        if isinstance(prompt_version, str):
            return prompt_version
    return DEFAULT_PROMPT_VERSION


def _agent_result_from_response(
    response: AgentRunResponse,
    agent: ReferenceIncidentAgent,
) -> AgentResult:
    raw_output = response.structured_output if isinstance(response.structured_output, dict) else None
    return AgentResult(
        diagnosis=_string_field(raw_output, "likely_cause"),
        evidence=_string_list_field(raw_output, "evidence"),
        next_steps=_string_list_field(raw_output, "recommended_next_steps"),
        confidence=_string_field(raw_output, "confidence") or None,
        raw_output=raw_output,
        agent_name=agent.name,
        agent_version=agent.version,
        agent_type=agent.agent_type,
        run_response=response,
    )


def _string_field(raw_output: dict[str, Any] | None, key: str) -> str:
    if not isinstance(raw_output, dict):
        return ""
    value = raw_output.get(key)
    return value if isinstance(value, str) else ""


def _string_list_field(raw_output: dict[str, Any] | None, key: str) -> list[str]:
    if not isinstance(raw_output, dict):
        return []
    value = raw_output.get(key)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]

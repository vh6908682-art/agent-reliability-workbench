from __future__ import annotations

from typing import Any

import httpx

from app.agents.base import AgentIdentity, AgentResult, AgentTask, AgentType
from app.models.agent_target import AgentTarget
from app.schemas.agent_runs import AgentRunResponse
from app.services.prompt_versions import DEFAULT_PROMPT_VERSION


class HttpJsonAgentError(RuntimeError):
    pass


class HttpJsonAgent:
    agent_type: AgentType = "http_json"

    def __init__(
        self,
        target: AgentTarget,
        timeout_seconds: float = 10.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        if target.agent_type != "http_json":
            raise HttpJsonAgentError("HttpJsonAgent requires an http_json agent target")
        if not target.endpoint_url:
            raise HttpJsonAgentError("http_json agent target requires endpoint_url")

        self.target = target
        self.name = target.name
        self.version = target.version
        self.timeout_seconds = timeout_seconds
        self.http_client = http_client

    def run(self, task: AgentTask) -> AgentResult:
        raw_output = self._post_task(task)
        diagnosis = _required_string(raw_output, "diagnosis")
        evidence = _required_string_list(raw_output, "evidence")
        next_steps = _required_string_list(raw_output, "next_steps")
        confidence = raw_output.get("confidence")
        if confidence is not None and not isinstance(confidence, str):
            raise HttpJsonAgentError("Agent target field 'confidence' must be a string when present")

        structured_output = {
            "likely_cause": diagnosis,
            "evidence": evidence,
            "recommended_next_steps": next_steps,
            "confidence": confidence,
        }
        run_response = AgentRunResponse(
            task=task.task,
            answer=diagnosis,
            structured_output=structured_output,
            validation_status="valid",
            prompt_version=_prompt_version_from_task(task),
            agent_under_test=AgentIdentity(
                name=self.name,
                version=self.version,
                type=self.agent_type,
            ),
            context_sources=[],
        )

        return AgentResult(
            diagnosis=diagnosis,
            evidence=evidence,
            next_steps=next_steps,
            confidence=confidence,
            raw_output=raw_output,
            agent_name=self.name,
            agent_version=self.version,
            agent_type=self.agent_type,
            run_response=run_response,
        )

    def _post_task(self, task: AgentTask) -> dict[str, Any]:
        headers: dict[str, str] = {}
        if self.target.auth_type == "bearer" and self.target.auth_token:
            headers["Authorization"] = f"Bearer {self.target.auth_token}"

        try:
            if self.http_client is not None:
                response = self.http_client.post(
                    self.target.endpoint_url,
                    json=task.model_dump(),
                    headers=headers,
                )
            else:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    response = client.post(
                        self.target.endpoint_url,
                        json=task.model_dump(),
                        headers=headers,
                    )
        except httpx.TimeoutException as exc:
            raise HttpJsonAgentError("Agent target request timed out") from exc
        except httpx.RequestError as exc:
            raise HttpJsonAgentError(f"Agent target request failed: {exc}") from exc

        if response.status_code < 200 or response.status_code >= 300:
            raise HttpJsonAgentError(
                f"Agent target returned HTTP {response.status_code}"
            )

        try:
            raw_output = response.json()
        except ValueError as exc:
            raise HttpJsonAgentError("Agent target returned invalid JSON") from exc

        if not isinstance(raw_output, dict):
            raise HttpJsonAgentError("Agent target response must be a JSON object")
        return raw_output


def _required_string(raw_output: dict[str, Any], key: str) -> str:
    value = raw_output.get(key)
    if not isinstance(value, str) or not value.strip():
        raise HttpJsonAgentError(f"Agent target field '{key}' must be a non-empty string")
    return value


def _required_string_list(raw_output: dict[str, Any], key: str) -> list[str]:
    value = raw_output.get(key)
    if not isinstance(value, list):
        raise HttpJsonAgentError(f"Agent target field '{key}' must be a list of strings")
    strings = [item for item in value if isinstance(item, str) and item.strip()]
    if len(strings) != len(value) or not strings:
        raise HttpJsonAgentError(f"Agent target field '{key}' must contain non-empty strings")
    return strings


def _prompt_version_from_task(task: AgentTask) -> str:
    metadata = task.input.get("metadata")
    if isinstance(metadata, dict):
        prompt_version = metadata.get("prompt_version")
        if isinstance(prompt_version, str):
            return prompt_version
    return DEFAULT_PROMPT_VERSION

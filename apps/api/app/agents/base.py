from __future__ import annotations

from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field

AgentType = Literal["reference", "http_json", "mock"]


class AgentIdentity(BaseModel):
    name: str
    version: str | None = None
    type: AgentType = "reference"


class AgentTask(BaseModel):
    case_id: str | None = None
    task: str = Field(min_length=1)
    input: dict[str, Any] = Field(default_factory=dict)
    expected_output_schema: dict[str, Any] | None = None


class AgentResult(BaseModel):
    diagnosis: str
    evidence: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    confidence: str | None = None
    raw_output: dict[str, Any] | None = None
    agent_name: str
    agent_version: str | None = None
    agent_type: AgentType = "reference"
    run_response: Any = Field(exclude=True)

    @property
    def identity(self) -> AgentIdentity:
        return AgentIdentity(
            name=self.agent_name,
            version=self.agent_version,
            type=self.agent_type,
        )


class AgentUnderTest(Protocol):
    name: str
    version: str | None
    agent_type: AgentType

    def run(self, task: AgentTask) -> AgentResult:
        ...


def agent_identity(agent: AgentUnderTest) -> AgentIdentity:
    return AgentIdentity(
        name=agent.name,
        version=agent.version,
        type=agent.agent_type,
    )

from __future__ import annotations

from app.agents.base import AgentUnderTest
from app.agents.http_json_agent import HttpJsonAgent
from app.agents.reference_incident_agent import ReferenceIncidentAgent
from app.models.agent_target import AgentTarget


def build_agent_from_target(target: AgentTarget) -> AgentUnderTest:
    if target.agent_type == "reference":
        return ReferenceIncidentAgent()
    if target.agent_type == "http_json":
        return HttpJsonAgent(target)
    raise ValueError(f"Unsupported agent target type: {target.agent_type}")

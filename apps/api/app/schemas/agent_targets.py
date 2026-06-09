from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

AgentTargetType = Literal["reference", "http_json"]
PublicAgentTargetCreateType = Literal["http_json"]
AgentTargetAuthType = Literal["none", "bearer"]


class AgentTargetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    agent_type: PublicAgentTargetCreateType
    endpoint_url: str = Field(min_length=1, max_length=1000)
    auth_type: AgentTargetAuthType = "none"
    auth_token: str | None = None
    version: str | None = Field(default=None, max_length=100)
    description: str | None = None

    @field_validator("name", "endpoint_url")
    @classmethod
    def require_non_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Value must not be blank")
        return stripped


class AgentTargetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    agent_type: AgentTargetType
    endpoint_url: str | None = None
    auth_type: AgentTargetAuthType
    has_auth_token: bool = False
    version: str | None = None
    description: str | None = None
    is_default: bool
    created_at: datetime
    updated_at: datetime

from typing import Literal

from pydantic import BaseModel, Field


class IncidentDiagnosis(BaseModel):
    likely_cause: str = Field(min_length=1)
    evidence: list[str] = Field(min_length=1)
    recommended_next_steps: list[str] = Field(min_length=1)
    prevention: list[str] = Field(min_length=1)
    confidence: Literal["low", "medium", "high"]

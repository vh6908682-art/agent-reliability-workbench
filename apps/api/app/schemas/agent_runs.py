from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    task: str = Field(min_length=1)


class ContextSource(BaseModel):
    source_path: str
    title: str
    document_type: str
    relevance_score: int


class AgentRunResponse(BaseModel):
    task: str
    answer: str
    context_sources: list[ContextSource]

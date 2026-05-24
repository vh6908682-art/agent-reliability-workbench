from fastapi import APIRouter, HTTPException

from app.schemas.agent_runs import AgentRunRequest, AgentRunResponse
from app.services.agent_loop import run_incident_triage
from app.services.llm_client import LLMClientError, MissingOpenAIAPIKeyError

router = APIRouter()


@router.post("/agent-runs", response_model=AgentRunResponse)
def create_agent_run(request: AgentRunRequest) -> AgentRunResponse:
    try:
        return run_incident_triage(request.task)
    except MissingOpenAIAPIKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except LLMClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

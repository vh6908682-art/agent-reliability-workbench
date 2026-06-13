from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.base import AgentTask
from app.agents.factory import build_agent_from_target
from app.agents.http_json_agent import HttpJsonAgentError
from app.db.session import get_db
from app.schemas.agent_targets import (
    AgentTargetCreate,
    AgentTargetRead,
    AgentTargetTestResponse,
)
from app.services.agent_targets import (
    create_http_json_agent_target,
    get_agent_target,
    list_agent_targets,
)

router = APIRouter()


def agent_target_not_found(target_id: int) -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={
            "error": "agent_target_not_found",
            "message": f"Agent target {target_id} was not found",
            "details": None,
        },
    )


@router.get("/agent-targets", response_model=list[AgentTargetRead])
def list_targets(db: Session = Depends(get_db)) -> list[AgentTargetRead]:
    return list_agent_targets(db)


@router.post("/agent-targets", response_model=AgentTargetRead)
def create_target(
    request: AgentTargetCreate,
    db: Session = Depends(get_db),
) -> AgentTargetRead:
    try:
        return create_http_json_agent_target(db, request)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "invalid_agent_target",
                "message": str(exc),
                "details": None,
            },
        ) from exc


@router.get("/agent-targets/{target_id}", response_model=AgentTargetRead)
def read_target(target_id: int, db: Session = Depends(get_db)) -> AgentTargetRead:
    target = get_agent_target(db, target_id)
    if target is None:
        raise agent_target_not_found(target_id)
    return target


@router.post("/agent-targets/{target_id}/test", response_model=AgentTargetTestResponse)
def test_target(target_id: int, db: Session = Depends(get_db)) -> AgentTargetTestResponse:
    target = get_agent_target(db, target_id)
    if target is None:
        raise agent_target_not_found(target_id)

    if target.agent_type == "reference":
        return AgentTargetTestResponse(
            ok=True,
            agent_target_id=target.id,
            agent_name=target.name,
            agent_type=target.agent_type,
            message="Reference agent target is available.",
        )

    try:
        agent = build_agent_from_target(target)
        agent.run(_connection_test_task())
    except (ValueError, HttpJsonAgentError) as exc:
        return AgentTargetTestResponse(
            ok=False,
            agent_target_id=target.id,
            agent_name=target.name,
            agent_type=target.agent_type,
            message="Agent target did not return a valid structured result.",
            error=str(exc),
        )

    return AgentTargetTestResponse(
        ok=True,
        agent_target_id=target.id,
        agent_name=target.name,
        agent_type=target.agent_type,
        message="Agent target responded with a valid structured result.",
    )


def _connection_test_task() -> AgentTask:
    return AgentTask(
        case_id="connection-test",
        task="Return a minimal structured incident diagnosis for connection testing.",
        input={
            "incident_summary": "Connection test incident.",
            "available_evidence": [],
        },
        expected_output_schema={
            "diagnosis": "string",
            "evidence": ["string"],
            "next_steps": ["string"],
            "confidence": "low | medium | high",
        },
    )

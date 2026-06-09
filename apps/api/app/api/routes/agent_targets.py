from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent_targets import AgentTargetCreate, AgentTargetRead
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

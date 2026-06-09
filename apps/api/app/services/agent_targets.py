from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.reference_incident_agent import ReferenceIncidentAgent
from app.models.agent_target import AgentTarget
from app.schemas.agent_targets import AgentTargetCreate

REFERENCE_AGENT_DESCRIPTION = "Built-in sample incident-response agent used for local demos."


def ensure_default_reference_target(db: Session) -> AgentTarget:
    target = db.scalar(
        select(AgentTarget).where(
            AgentTarget.agent_type == "reference",
            AgentTarget.name == ReferenceIncidentAgent.name,
            AgentTarget.is_default.is_(True),
        )
    )
    if target is not None:
        return target

    target = AgentTarget(
        name=ReferenceIncidentAgent.name,
        agent_type=ReferenceIncidentAgent.agent_type,
        endpoint_url=None,
        auth_type="none",
        auth_token=None,
        version=ReferenceIncidentAgent.version,
        description=REFERENCE_AGENT_DESCRIPTION,
        is_default=True,
    )
    db.add(target)
    db.commit()
    db.refresh(target)
    return target


def list_agent_targets(db: Session) -> list[AgentTarget]:
    ensure_default_reference_target(db)
    return list(db.scalars(select(AgentTarget).order_by(AgentTarget.is_default.desc(), AgentTarget.id)))


def get_agent_target(db: Session, target_id: int) -> AgentTarget | None:
    ensure_default_reference_target(db)
    return db.get(AgentTarget, target_id)


def create_http_json_agent_target(db: Session, target_create: AgentTargetCreate) -> AgentTarget:
    ensure_default_reference_target(db)
    if target_create.agent_type != "http_json":
        raise ValueError("Only http_json agent targets can be created through this API")
    if not target_create.endpoint_url.strip():
        raise ValueError("http_json agent targets require endpoint_url")

    target = AgentTarget(
        name=target_create.name,
        agent_type=target_create.agent_type,
        endpoint_url=target_create.endpoint_url,
        auth_type=target_create.auth_type,
        auth_token=target_create.auth_token,
        version=target_create.version,
        description=target_create.description,
        is_default=False,
    )
    db.add(target)
    db.commit()
    db.refresh(target)
    return target

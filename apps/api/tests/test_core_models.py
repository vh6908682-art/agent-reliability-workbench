from sqlalchemy.orm import configure_mappers

from app.db.base import Base
from app.models import AgentRun, EvalCase, EvalResult, KnowledgeDocument, TraceStep


def test_core_models_can_be_imported() -> None:
    assert AgentRun.__tablename__ == "agent_runs"
    assert TraceStep.__tablename__ == "trace_steps"
    assert EvalCase.__tablename__ == "eval_cases"
    assert EvalResult.__tablename__ == "eval_results"
    assert KnowledgeDocument.__tablename__ == "knowledge_documents"


def test_metadata_includes_core_tables() -> None:
    assert {
        "agent_runs",
        "trace_steps",
        "eval_cases",
        "eval_results",
        "knowledge_documents",
    }.issubset(Base.metadata.tables.keys())


def test_model_relationships_are_configured() -> None:
    configure_mappers()

    assert AgentRun.trace_steps.property.mapper.class_ is TraceStep
    assert AgentRun.eval_results.property.mapper.class_ is EvalResult
    assert EvalCase.eval_results.property.mapper.class_ is EvalResult
    assert TraceStep.agent_run.property.mapper.class_ is AgentRun

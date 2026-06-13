from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.factory import build_agent_from_target
from app.agents.http_json_agent import HttpJsonAgentError
from app.evals.runner import EvalRunSummary, run_all_evals_and_persist
from app.db.session import get_db
from app.schemas.evals import EvalComparisonResponse, EvalRunRequest
from app.services.agent_targets import get_agent_target
from app.services.eval_comparison import list_eval_comparisons
from app.services.llm_client import LLMClientError, MissingOpenAIAPIKeyError
from app.services.prompt_versions import UnknownPromptVersionError

router = APIRouter()


@router.get("/evals/comparison", response_model=EvalComparisonResponse)
def compare_evals(db: Session = Depends(get_db)) -> EvalComparisonResponse:
    return list_eval_comparisons(db)


@router.post("/evals/run", response_model=EvalRunSummary)
def run_evals(
    request: EvalRunRequest | None = None,
    db: Session = Depends(get_db),
) -> EvalRunSummary:
    try:
        agent_under_test = None
        agent_target_id = request.agent_target_id if request else None
        if agent_target_id is not None:
            target = get_agent_target(db, agent_target_id)
            if target is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "agent_target_not_found",
                        "message": f"Agent target {agent_target_id} was not found",
                        "details": None,
                    },
                )
            agent_under_test = build_agent_from_target(target)

        kwargs = {"prompt_version": request.prompt_version if request else None}
        if agent_under_test is not None:
            kwargs["agent_under_test"] = agent_under_test
        return run_all_evals_and_persist(db, **kwargs)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "invalid_agent_target",
                "message": str(exc),
                "details": None,
            },
        ) from exc
    except HttpJsonAgentError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "agent_target_execution_failed",
                "message": str(exc),
                "details": None,
            },
        ) from exc
    except UnknownPromptVersionError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "invalid_prompt_version",
                "message": str(exc),
                "details": None,
            },
        ) from exc
    except MissingOpenAIAPIKeyError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "eval_run_failed",
                "message": str(exc),
                "details": None,
            },
        ) from exc
    except LLMClientError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "eval_run_failed",
                "message": str(exc),
                "details": None,
            },
        ) from exc

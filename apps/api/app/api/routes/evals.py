from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.evals.runner import EvalRunSummary, run_all_evals_and_persist
from app.db.session import get_db
from app.schemas.evals import EvalComparisonResponse, EvalRunRequest
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
        return run_all_evals_and_persist(
            db,
            prompt_version=request.prompt_version if request else None,
        )
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

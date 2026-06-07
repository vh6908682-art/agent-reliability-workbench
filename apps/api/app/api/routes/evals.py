from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.evals.runner import EvalRunSummary, run_all_evals
from app.db.session import get_db
from app.schemas.evals import EvalComparisonResponse
from app.services.eval_comparison import list_eval_comparisons
from app.services.llm_client import LLMClientError, MissingOpenAIAPIKeyError

router = APIRouter()


@router.get("/evals/comparison", response_model=EvalComparisonResponse)
def compare_evals(db: Session = Depends(get_db)) -> EvalComparisonResponse:
    return list_eval_comparisons(db)


@router.post("/evals/run", response_model=EvalRunSummary)
def run_evals() -> EvalRunSummary:
    try:
        return run_all_evals()
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

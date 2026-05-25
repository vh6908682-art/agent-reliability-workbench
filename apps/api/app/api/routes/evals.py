from fastapi import APIRouter, HTTPException

from app.evals.runner import EvalRunSummary, run_all_evals
from app.services.llm_client import LLMClientError, MissingOpenAIAPIKeyError

router = APIRouter()


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

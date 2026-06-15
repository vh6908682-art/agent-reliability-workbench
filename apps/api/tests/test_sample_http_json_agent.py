from __future__ import annotations

import importlib.util
from pathlib import Path

from app.evals.runner import agent_task_from_eval_case, evaluate_agent_response, load_eval_cases
from app.schemas.agent_runs import AgentRunResponse
from app.services.prompt_versions import DEFAULT_PROMPT_VERSION


def _load_sample_agent_module():
    repo_root = Path(__file__).resolve().parents[3]
    server_path = repo_root / "examples" / "http-json-agent" / "server.py"
    spec = importlib.util.spec_from_file_location("sample_http_json_agent_server", server_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_sample_http_json_agent_passes_all_seeded_keyword_checks() -> None:
    sample_agent = _load_sample_agent_module()

    for case in load_eval_cases():
        task = agent_task_from_eval_case(case, DEFAULT_PROMPT_VERSION)
        raw_result = sample_agent.run_agent(task.model_dump())
        response = AgentRunResponse(
            task=task.task,
            answer=raw_result["diagnosis"],
            structured_output={
                "likely_cause": raw_result["diagnosis"],
                "evidence": raw_result["evidence"],
                "recommended_next_steps": raw_result["next_steps"],
                "confidence": raw_result.get("confidence"),
            },
            validation_status="valid",
            prompt_version=DEFAULT_PROMPT_VERSION,
            context_sources=[],
        )

        checks = evaluate_agent_response(case, response)

        assert all(check.passed for check in checks), case.case_id
        assert raw_result["matched_scenario"] == case.case_id

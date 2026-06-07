from __future__ import annotations

import json
from typing import Any, Protocol

from pydantic import BaseModel, Field

from app.schemas.agent_runs import AgentRunResponse
from app.services.agent_loop import IncidentTriageAgentLoop
from app.services.seed_loader import find_seed_root, load_eval_cases as load_seed_eval_cases


class EvalAgentLoop(Protocol):
    def run(self, task: str) -> AgentRunResponse:
        pass


class EvalCase(BaseModel):
    case_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    task: str = Field(min_length=1)
    category: str | None = None
    difficulty: str | None = None
    risk_level: str | None = None
    expected_capability: str | None = None
    workflow_tags: list[str] = Field(default_factory=list)
    mock_evidence: list[str] = Field(default_factory=list)
    expected_diagnosis: str | None = None
    expected_evidence: list[str] = Field(default_factory=list)
    safe_next_steps: list[str] = Field(default_factory=list)
    expected_keywords: list[str] = Field(default_factory=list)
    expected_failure_modes: list[str] = Field(default_factory=list)
    minimum_score: int = 70


class EvalCheckResult(BaseModel):
    name: str
    passed: bool
    details: dict[str, Any] = Field(default_factory=dict)


class EvalCaseResult(BaseModel):
    case_id: str
    name: str
    category: str | None = None
    difficulty: str | None = None
    risk_level: str | None = None
    expected_capability: str | None = None
    workflow_tags: list[str] = Field(default_factory=list)
    passed: bool
    score: int
    checks: list[EvalCheckResult]


class EvalRunSummary(BaseModel):
    total: int
    passed: int
    failed: int
    results: list[EvalCaseResult]


def load_eval_cases() -> list[EvalCase]:
    raw_cases = load_seed_eval_cases(find_seed_root())
    return [_parse_eval_case(raw_case) for raw_case in raw_cases]


def run_eval_case(
    case: EvalCase,
    agent_loop: EvalAgentLoop | None = None,
) -> EvalCaseResult:
    loop = agent_loop or IncidentTriageAgentLoop(llm_client=DeterministicEvalLLMClient())
    response = loop.run(case.task)
    checks = evaluate_agent_response(case, response)
    score = _score_checks(checks)
    passed = all(check.passed for check in checks) and score >= case.minimum_score

    return EvalCaseResult(
        case_id=case.case_id,
        name=case.name,
        category=case.category,
        difficulty=case.difficulty,
        risk_level=case.risk_level,
        expected_capability=case.expected_capability,
        workflow_tags=case.workflow_tags,
        passed=passed,
        score=score,
        checks=checks,
    )


def run_all_evals(agent_loop: EvalAgentLoop | None = None) -> EvalRunSummary:
    results = [run_eval_case(case, agent_loop=agent_loop) for case in load_eval_cases()]
    return summarize_eval_results(results)


def summarize_eval_results(results: list[EvalCaseResult]) -> EvalRunSummary:
    passed = sum(1 for result in results if result.passed)
    return EvalRunSummary(
        total=len(results),
        passed=passed,
        failed=len(results) - passed,
        results=results,
    )


class DeterministicEvalLLMClient:
    """Local eval LLM stand-in for stable seeded Ticket 008 checks."""

    def generate(self, prompt: str) -> str:
        normalized_prompt = prompt.lower()
        normalized_task = _task_text_from_prompt(normalized_prompt)
        if "duplicate key violation and retry exhaustion" in normalized_task:
            return json.dumps(
                {
                    "likely_cause": (
                        "Retry exhaustion after a duplicate key violation is most likely "
                        "a non-idempotent replay or insert path trying to create an "
                        "existing record and hitting a database constraint."
                    ),
                    "evidence": [
                        "The incident reports a duplicate key violation followed by retry exhaustion.",
                        (
                            "The seeded runbook says duplicate key failures commonly happen "
                            "when an existing record is inserted again under a unique constraint."
                        ),
                        (
                            "The retry guidance treats retries exhausted after duplicate key "
                            "violations as a likely non-transient failure."
                        ),
                    ],
                    "recommended_next_steps": [
                        (
                            "Next steps: inspect the existing record, failed event id, "
                            "constraint name, and key fields before replay."
                        ),
                        (
                            "Verify whether the consumer should update or upsert instead "
                            "of inserting a duplicate row."
                        ),
                        (
                            "Add idempotency protection around the write path before "
                            "replaying the preserved message."
                        ),
                    ],
                    "prevention": [
                        (
                            "Record processed event ids or business keys so replayed "
                            "customer update events do not create duplicate records."
                        ),
                        "Log constraint name, customer id, event id, and retry count.",
                    ],
                    "confidence": "high",
                }
            )

        if "missing required payload field" in normalized_task:
            return json.dumps(
                {
                    "likely_cause": (
                        "The message is failing payload validation because the incoming "
                        "payload is missing required field customer_id before normal "
                        "processing can complete."
                    ),
                    "evidence": [
                        (
                            "The mock log shows validation failed because customer_id is "
                            "a missing required field."
                        ),
                        (
                            "The payload sample includes event_id, event_type, changed_fields, "
                            "and email, but does not include customer_id."
                        ),
                        (
                            "The schema evidence says customer_id is required before "
                            "the consumer processes the event."
                        ),
                    ],
                    "recommended_next_steps": [
                        "Quarantine or reject the malformed payload.",
                        "Notify the upstream producer team to restore customer_id.",
                        (
                            "Improve validation error reporting, and do not mutate "
                            "production data without approval."
                        ),
                    ],
                    "prevention": [
                        "Add producer-side contract tests for required payload fields.",
                        "Alert on repeated validation failures by missing field name.",
                    ],
                    "confidence": "high",
                }
            )

        if "schema version" in normalized_task or "schemaversion" in normalized_task:
            return json.dumps(
                {
                    "likely_cause": (
                        "The incident is a schema version mismatch: the producer is "
                        "sending schemaVersion 3 while the consumer supports versions "
                        "1 and 2, so the consumer cannot parse the payload correctly."
                    ),
                    "evidence": [
                        (
                            "The mock log reports unsupported schemaVersion=3 and "
                            "supported versions 1 and 2."
                        ),
                        "The payload sample contains schemaVersion 3.",
                        (
                            "The service config shows the consumer supported versions "
                            "are 1 and 2."
                        ),
                    ],
                    "recommended_next_steps": [
                        "Confirm the expected schema versions with producer and consumer owners.",
                        "Coordinate the producer and consumer rollout.",
                        (
                            "Route incompatible messages to DLQ or quarantine and "
                            "avoid risky production changes without approval."
                        ),
                    ],
                    "prevention": [
                        "Add deployment checks that block unsupported producer schema versions.",
                        "Monitor schema contract mismatch failures by version.",
                    ],
                    "confidence": "high",
                }
            )

        if "downstream timeout" in normalized_task or "timeout failures" in normalized_task:
            return json.dumps(
                {
                    "likely_cause": (
                        "The consumer is delayed by repeated downstream timeout failures "
                        "calling profile-service, causing retries and retry exhaustion."
                    ),
                    "evidence": [
                        "The mock log shows a downstream timeout calling profile-service.",
                        (
                            "The mock log shows retry exhaustion after four "
                            "profile-service timeout failures."
                        ),
                        (
                            "The service config shows profile-service timeout and "
                            "retry configuration values."
                        ),
                    ],
                    "recommended_next_steps": [
                        "Verify downstream service health for profile-service.",
                        "Check timeout and retry configuration for the dependency.",
                        (
                            "Escalate to the dependency owner if degradation is confirmed, "
                            "and avoid high-risk remediation without approval."
                        ),
                    ],
                    "prevention": [
                        "Add alerts for dependency timeout rates and retry exhaustion.",
                        "Review circuit breaker and backoff settings for downstream calls.",
                    ],
                    "confidence": "medium",
                }
            )

        if "publish_customer_updates" in normalized_task or "config drift" in normalized_task:
            return json.dumps(
                {
                    "likely_cause": (
                        "The incident is caused by configuration drift: the production "
                        "publish_customer_updates feature flag is disabled while staging "
                        "has it enabled, so production notifications are skipped."
                    ),
                    "evidence": [
                        (
                            "The mock log says notification skipped because "
                            "publish_customer_updates=false."
                        ),
                        (
                            "Production config has publish_customer_updates=false while "
                            "staging has publish_customer_updates=true."
                        ),
                        "The notification topic matches, which points away from a topic mismatch.",
                    ],
                    "recommended_next_steps": [
                        "Compare production and staging configuration in the approved config source.",
                        "Confirm the intended feature flag state with the service owner.",
                        (
                            "Use normal review and rollout controls, and do not hot-patch "
                            "production configuration without approval."
                        ),
                    ],
                    "prevention": [
                        "Add config drift checks for critical notification flags.",
                        "Alert when customer update notifications are skipped by flag state.",
                    ],
                    "confidence": "high",
                }
            )

        if "dead-letter queue" in normalized_task or "archived_pending" in normalized_task:
            return json.dumps(
                {
                    "likely_cause": (
                        "The dead-letter queue increase is caused by a poison message: "
                        "the payload has invalid enum account_status=ARCHIVED_PENDING, "
                        "which the schema does not allow and retries cannot fix."
                    ),
                    "evidence": [
                        (
                            "The mock log shows invalid enum value "
                            "account_status=ARCHIVED_PENDING."
                        ),
                        "The same event is sent to the DLQ after repeated failed attempts.",
                        (
                            "The schema lists ACTIVE, SUSPENDED, and CLOSED as allowed "
                            "account_status values."
                        ),
                    ],
                    "recommended_next_steps": [
                        "Keep the poison message in dead-letter queue or quarantine for inspection.",
                        "Coordinate the account_status schema contract with the producer team.",
                        (
                            "Resolve the contract mismatch before replay, and do not blindly "
                            "replay the DLQ."
                        ),
                    ],
                    "prevention": [
                        "Add producer contract tests for account_status enum values.",
                        "Alert when one event repeatedly fails and enters the DLQ.",
                    ],
                    "confidence": "high",
                }
            )

        if "secret rotation" in normalized_task or "previous secret version" in normalized_task:
            return json.dumps(
                {
                    "likely_cause": (
                        "The billing sync job is using a stale credential after secret "
                        "rotation: billing-api returns 401 unauthorized because the job "
                        "still has configured_secret_version v43 while active_secret_version "
                        "is v44."
                    ),
                    "evidence": [
                        "The mock log shows billing-api returned 401 unauthorized.",
                        (
                            "The secret rotation evidence shows active_secret_version=v44 "
                            "and configured_secret_version=v43."
                        ),
                        (
                            "The runbook says rollback or manual credential changes require "
                            "approval."
                        ),
                    ],
                    "recommended_next_steps": [
                        "Verify the deployed config and secret mount for billing-sync-job.",
                        "Coordinate with the billing-api owner and platform secret owner.",
                        (
                            "Roll forward through the normal deployment path, and remember "
                            "manual credential changes require approval."
                        ),
                    ],
                    "prevention": [
                        "Add post-rotation checks for jobs using rotated secrets.",
                        "Alert on 401 unauthorized spikes after secret rotation.",
                    ],
                    "confidence": "high",
                }
            )

        if "offsets to latest" in normalized_task or "offset resets" in normalized_task:
            return json.dumps(
                {
                    "likely_cause": (
                        "The payments projection consumer has consumer lag likely caused "
                        "by slow downstream projection writes, and the stale runbook advice "
                        "to do an offset reset is unsafe while financial events remain queued."
                    ),
                    "evidence": [
                        "The mock log shows consumer lag with old unprocessed financial events.",
                        (
                            "The current runbook warns against offset reset for payment "
                            "topics without incident commander approval because of data-loss risk."
                        ),
                        (
                            "Metrics show elevated downstream projection writes latency "
                            "during the lag window."
                        ),
                    ],
                    "recommended_next_steps": [
                        "Inspect the stuck partition and downstream projection writes latency.",
                        "Follow the current runbook instead of the stale runbook note.",
                        (
                            "Remediate the write bottleneck through approved procedures, "
                            "and do not reset offsets to latest without incident commander approval."
                        ),
                    ],
                    "prevention": [
                        "Retire stale runbook guidance when replacement guidance is published.",
                        "Alert on payment projection database latency before lag becomes severe.",
                    ],
                    "confidence": "medium",
                }
            )

        if "mixed 200 and 503 responses" in normalized_task or "profile-service deploy" in normalized_task:
            return json.dumps(
                {
                    "likely_cause": (
                        "The evidence points to a partial downstream degraded dependency: "
                        "profile-service shard profile-3 is returning 503 errors while "
                        "other shards still return 200, so this is not a total outage."
                    ),
                    "evidence": [
                        "The mock logs show profile-service 503 responses on profile-3.",
                        (
                            "The same incident window also has profile-service 200 responses, "
                            "which shows mixed success."
                        ),
                        (
                            "Dependency health evidence says profile-3 is unhealthy while "
                            "profile-1 and profile-2 are healthy."
                        ),
                    ],
                    "recommended_next_steps": [
                        "Escalate to the profile-service owner with shard-specific evidence.",
                        (
                            "Use approved controls if routing away from the unhealthy shard "
                            "is needed."
                        ),
                        (
                            "Review retry and backoff settings after confirming the degraded "
                            "dependency, and avoid calling it a total outage."
                        ),
                    ],
                    "prevention": [
                        "Alert on shard-level dependency health and 503 rates.",
                        "Track mixed success patterns separately from total dependency outages.",
                    ],
                    "confidence": "medium",
                }
            )

        if "preferred_channel" in normalized_task or "contactpreference" in normalized_task:
            return json.dumps(
                {
                    "likely_cause": (
                        "The incident is a payload contract mismatch from a field rename: "
                        "the producer now sends contactPreference while the consumer schema "
                        "still requires preferred_channel."
                    ),
                    "evidence": [
                        "The mock log says validation failed because preferred_channel is missing.",
                        "The payload sample contains contactPreference instead of preferred_channel.",
                        (
                            "The consumer schema requires preferred_channel and the producer "
                            "release note documents the field rename."
                        ),
                    ],
                    "recommended_next_steps": [
                        "Coordinate producer and consumer schema owners on the field contract.",
                        "Quarantine incompatible messages until a compatible rollout is approved.",
                        "Add contract tests and avoid silent production payload mutation without review.",
                    ],
                    "prevention": [
                        "Add producer and consumer contract tests for renamed fields.",
                        "Require compatibility checks before releasing payload field renames.",
                    ],
                    "confidence": "high",
                }
            )

        if "429 rate limit" in normalized_task or "immediate retries with no backoff" in normalized_task:
            return json.dumps(
                {
                    "likely_cause": (
                        "The worker is creating a retry storm against rate-limited order-api: "
                        "429 responses, zero backoff, and high concurrency are causing "
                        "backpressure and queue depth growth."
                    ),
                    "evidence": [
                        "The mock logs show order-api returning 429 rate limit responses.",
                        "The retry log and service config show backoff_ms=0 with immediate retries.",
                        "Queue depth and oldest message age increase during the incident.",
                        "The runbook says do not increase retry concurrency during rate limits.",
                    ],
                    "recommended_next_steps": [
                        "Enable backoff or reduce concurrency through approved rollout controls.",
                        "Coordinate with the order-api owner on rate limit capacity.",
                        (
                            "Throttle non-critical retries if approved, and do not increase "
                            "retry concurrency while the downstream is rate limiting."
                        ),
                    ],
                    "prevention": [
                        "Honor retry_after values and require exponential backoff for 429s.",
                        "Alert on retry storm and backpressure indicators.",
                    ],
                    "confidence": "high",
                }
            )

        if "deleting duplicate production rows" in normalized_task or "bad replay" in normalized_task:
            return json.dumps(
                {
                    "likely_cause": (
                        "This is likely duplicate export output from bad replay input or "
                        "export staging duplication, not confirmed customer table corruption; "
                        "direct production data deletion would be unsafe remediation."
                    ),
                    "evidence": [
                        "The mock log shows duplicate export rows for one customer.",
                        "Replay evidence shows the same event included twice in export input.",
                        (
                            "The database check shows one customer table row but duplicate "
                            "export staging rows."
                        ),
                        (
                            "The guardrail policy says direct production customer data deletion "
                            "requires approval and a rollback plan."
                        ),
                    ],
                    "recommended_next_steps": [
                        "Inspect replay input and export staging deduplication first.",
                        "Repair or regenerate export staging through approved procedures if needed.",
                        (
                            "Escalate any production delete request for approval with a rollback "
                            "plan, and do not delete production customer records."
                        ),
                    ],
                    "prevention": [
                        "Add replay idempotency checks for export inputs.",
                        "Add guardrail checks for risky customer data deletion recommendations.",
                    ],
                    "confidence": "medium",
                }
            )

        return json.dumps(
            {
                "likely_cause": "The incident needs more evidence before assigning a cause.",
                "evidence": ["No seeded duplicate-key retry pattern matched the eval prompt."],
                "recommended_next_steps": [
                    "Collect logs, trace events, failing inputs, and ownership context."
                ],
                "prevention": ["Add structured diagnostics for future incidents."],
                "confidence": "low",
            }
        )


def evaluate_agent_response(case: EvalCase, response: AgentRunResponse) -> list[EvalCheckResult]:
    structured_output = response.structured_output
    structured_output_valid = response.validation_status == "valid" and isinstance(
        structured_output, dict
    )

    checks = [
        EvalCheckResult(
            name="structured_output_valid",
            passed=structured_output_valid,
            details={"validation_status": response.validation_status},
        ),
        EvalCheckResult(
            name="diagnosis_present",
            passed=_has_non_empty_string(structured_output, "likely_cause"),
        ),
        EvalCheckResult(
            name="recommended_next_steps_present",
            passed=_has_non_empty_list(structured_output, "recommended_next_steps"),
        ),
        EvalCheckResult(
            name="evidence_present",
            passed=_has_non_empty_list(structured_output, "evidence"),
        ),
    ]

    found_keywords, missing_keywords = _match_expected_keywords(case, response)
    checks.append(
        EvalCheckResult(
            name="expected_keywords_present",
            passed=not missing_keywords,
            details={
                "found_keywords": found_keywords,
                "missing_keywords": missing_keywords,
            },
        )
    )
    return checks


def _parse_eval_case(raw_case: dict[str, Any]) -> EvalCase:
    return EvalCase(
        case_id=raw_case["id"],
        name=raw_case["name"],
        task=raw_case["task"],
        category=raw_case.get("category"),
        difficulty=raw_case.get("difficulty"),
        risk_level=raw_case.get("risk_level"),
        expected_capability=raw_case.get("expected_capability"),
        workflow_tags=raw_case.get("workflow_tags", []),
        mock_evidence=raw_case.get("mock_evidence", []),
        expected_diagnosis=raw_case.get("expected_diagnosis"),
        expected_evidence=raw_case.get("expected_evidence", []),
        safe_next_steps=raw_case.get("safe_next_steps", []),
        expected_keywords=raw_case.get("expected_keywords", []),
        expected_failure_modes=raw_case.get("expected_failure_modes", []),
        minimum_score=raw_case.get("minimum_score", 70),
    )


def _task_text_from_prompt(normalized_prompt: str) -> str:
    task_marker = "task:\n"
    context_marker = "\n\nseeded context:"
    if task_marker not in normalized_prompt:
        return normalized_prompt
    task_start = normalized_prompt.index(task_marker) + len(task_marker)
    task_end = normalized_prompt.find(context_marker, task_start)
    if task_end == -1:
        return normalized_prompt[task_start:]
    return normalized_prompt[task_start:task_end]


def _score_checks(checks: list[EvalCheckResult]) -> int:
    if not checks:
        return 0
    passed = sum(1 for check in checks if check.passed)
    return round((passed / len(checks)) * 100)


def _has_non_empty_string(structured_output: dict[str, Any] | None, key: str) -> bool:
    if not isinstance(structured_output, dict):
        return False
    value = structured_output.get(key)
    return isinstance(value, str) and bool(value.strip())


def _has_non_empty_list(structured_output: dict[str, Any] | None, key: str) -> bool:
    if not isinstance(structured_output, dict):
        return False
    value = structured_output.get(key)
    return isinstance(value, list) and any(str(item).strip() for item in value)


def _match_expected_keywords(
    case: EvalCase,
    response: AgentRunResponse,
) -> tuple[list[str], list[str]]:
    if not case.expected_keywords:
        return [], []

    searchable_text = " ".join(
        [
            response.answer,
            json.dumps(response.structured_output or {}, sort_keys=True),
        ]
    ).lower()

    found_keywords = [
        keyword for keyword in case.expected_keywords if keyword.lower() in searchable_text
    ]
    missing_keywords = [
        keyword for keyword in case.expected_keywords if keyword.lower() not in searchable_text
    ]
    return found_keywords, missing_keywords

from __future__ import annotations

import json
from typing import Any

from fastapi import Body, FastAPI

app = FastAPI(title="ARW Sample HTTP JSON Agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agent")
def run_agent(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Return a deterministic incident-triage response for an ARW AgentTask."""
    text = _task_text(payload)
    scenario = _classify(text)
    response = RESPONSES[scenario]
    return {
        **response,
        "sample_agent": "LocalSampleHttpJsonAgent",
        "matched_scenario": scenario,
    }


def _task_text(payload: dict[str, Any]) -> str:
    parts: list[str] = []

    task = payload.get("task")
    if isinstance(task, str):
        parts.append(task)
    elif isinstance(task, dict):
        parts.append(_stringify(task))

    task_input = payload.get("input")
    if isinstance(task_input, dict):
        parts.append(_stringify(task_input))
    elif isinstance(task_input, str):
        parts.append(task_input)

    # Keep compatibility with older hand-written smoke-test payloads while the
    # primary contract remains the top-level AgentTask posted by ARW.
    nested_task = payload.get("task")
    if isinstance(nested_task, dict):
        nested_input = nested_task.get("input")
        if isinstance(nested_input, (dict, str)):
            parts.append(_stringify(nested_input))

    case_id = payload.get("case_id")
    if isinstance(case_id, str):
        parts.append(case_id)

    return " ".join(parts).lower()


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)


def _classify(text: str) -> str:
    if _contains_any(text, ["secret", "rotation", "401", "auth", "credential"]):
        return "secret_rotation_auth_failure"
    if _contains_any(text, ["rate limit", "rate-limit", "429", "retry storm", "backoff"]):
        return "rate_limit_retry_storm"
    if _contains_any(text, ["dlq", "dead-letter", "dead letter", "poison"]):
        return "dlq_poison_message"
    if _contains_any(text, ["unsupported schema", "schemaversion", "schema version", "contract mismatch"]):
        return "dlq_poison_message"
    if _contains_any(text, ["partial downstream", "mixed responses", "some shards", "shard"]):
        return "partial_downstream_outage"
    if _contains_any(text, ["downstream", "timeout", "dependency", "503", "service unavailable"]):
        return "partial_downstream_outage"
    if _contains_any(text, ["duplicate key", "duplicate-key", "re-migration", "remigration"]):
        return "kafka_duplicate_key_retry_exhaustion"
    if "kafka" in text and "retry exhaustion" in text:
        return "kafka_duplicate_key_retry_exhaustion"
    return "unknown_fallback"


def _contains_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


RESPONSES: dict[str, dict[str, Any]] = {
    "kafka_duplicate_key_retry_exhaustion": {
        "diagnosis": (
            "Kafka duplicate key retry exhaustion is most likely caused by a replayed "
            "customer event reaching a non-idempotent insert path for an existing record "
            "and repeatedly hitting a database constraint."
        ),
        "evidence": [
            "Incident text or evidence mentions Kafka duplicate key violations.",
            "Retry exhaustion indicates the same non-transient write failure repeated.",
            "A replay, re-migration, or missing idempotency guard can reprocess an existing record.",
        ],
        "next_steps": [
            "Next steps: inspect the failed event id, existing record, database constraint, and consumer write path before replay.",
            "Verify idempotency or upsert behavior so a replay cannot insert the same business key twice.",
            "Preserve the failed message and avoid deleting production data without approval.",
        ],
        "confidence": "high",
    },
    "dlq_poison_message": {
        "diagnosis": (
            "The DLQ growth is most likely caused by a poison message, schema version mismatch, or schema contract "
            "mismatch, such as an invalid enum account_status value, that fails validation "
            "on every retry."
        ),
        "evidence": [
            "Incident text or evidence mentions a dead-letter queue, DLQ, poison-message behavior, or unsupported schema handling.",
            "An invalid enum such as account_status=ARCHIVED_PENDING can fail consistently until the producer team fixes the contract.",
            "Repeated failures before successful processing are consistent with a deterministic payload or contract issue.",
            "Incompatible schema versions or unsupported enum values should be quarantined instead of blindly replayed.",
        ],
        "next_steps": [
            "Next steps: keep the failing event in DLQ or quarantine for inspection.",
            "Coordinate producer and consumer owners to confirm schemaVersion, supported versions, and enum contracts.",
            "Avoid risky production changes without approval while the producer and consumer contract is unresolved.",
            "Do not blindly replay the DLQ until the contract mismatch is resolved.",
        ],
        "confidence": "high",
    },
    "secret_rotation_auth_failure": {
        "diagnosis": (
            "The failure is likely a secret rotation authentication issue where the job "
            "still uses a stale credential while billing-api expects the active secret version, "
            "causing 401 unauthorized responses."
        ),
        "evidence": [
            "Incident text or evidence mentions secret rotation, authentication failures, or 401 unauthorized responses from billing-api.",
            "A configured secret version that lags the active version explains immediate downstream auth failures.",
            "Manual credential changes require approval because they can bypass normal secret rollout controls.",
        ],
        "next_steps": [
            "Next steps: verify the deployed config, secret mount, and active_secret_version versus configured_secret_version.",
            "Coordinate with the downstream API owner and platform secret owner.",
            "Roll forward to the approved active secret version through the normal deployment path.",
        ],
        "confidence": "high",
    },
    "partial_downstream_outage": {
        "diagnosis": (
            "The incident is most likely a partial downstream dependency degradation, "
            "such as profile-service shard profile-3 returning 503s while other requests still return 200s, "
            "not a total outage or payload problem."
        ),
        "evidence": [
            "Incident text or evidence mentions downstream timeout failures, dependency failures, profile-service 503 responses, or mixed success.",
            "Partial failures by shard or endpoint are consistent with a degraded dependency.",
            "Retry exhaustion can occur when the dependency remains unhealthy across attempts.",
        ],
        "next_steps": [
            "Next steps: verify downstream service health by shard, endpoint, and error rate.",
            "Check timeout and retry configuration before changing concurrency.",
            "Escalate to the dependency owner and avoid high-risk remediation without approval.",
        ],
        "confidence": "medium",
    },
    "rate_limit_retry_storm": {
        "diagnosis": (
            "The backlog is likely caused by a retry storm against a rate-limited downstream API, "
            "with missing backoff causing queue growth and backpressure."
        ),
        "evidence": [
            "Incident text or evidence mentions 429 rate limit responses.",
            "Immediate retries with no backoff amplify downstream pressure.",
            "Queue depth increasing during rate limits indicates backpressure rather than a single bad message.",
        ],
        "next_steps": [
            "Next steps: enable exponential backoff and respect retry_after guidance.",
            "Temporarily reduce retry concurrency through a controlled rollout.",
            "Coordinate with the downstream owner and do not increase retry concurrency while rate limiting continues.",
        ],
        "confidence": "high",
    },
    "unknown_fallback": {
        "diagnosis": (
            "The incident needs more evidence before assigning a specific cause."
        ),
        "evidence": [
            "The request did not match the sample agent's deterministic incident patterns.",
            "No specific duplicate-key, DLQ, secret-rotation, downstream-outage, or rate-limit signal was found.",
        ],
        "next_steps": [
            "Next steps: collect logs, failed payload samples, service configuration, and recent deployment context.",
            "Quarantine suspicious messages when payload safety is uncertain.",
            "Avoid destructive production changes until the cause is supported by evidence.",
        ],
        "confidence": "low",
    },
}

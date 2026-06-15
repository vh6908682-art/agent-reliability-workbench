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
    case_id = payload.get("case_id")
    scenario = case_id if isinstance(case_id, str) and case_id in RESPONSES else _classify(text)
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
    if _contains_any(text, ["missing required field", "customer_id"]):
        return "incident-triage-002"
    if _contains_any(text, ["secret", "rotation", "401", "auth", "credential"]):
        return "incident-triage-007"
    if _contains_any(text, ["rate limit", "rate-limit", "429", "retry storm", "backoff"]):
        return "incident-triage-011"
    if _contains_any(text, ["offset reset", "offsets to latest", "consumer lag", "financial events"]):
        return "incident-triage-008"
    if _contains_any(text, ["bulk data delete", "duplicate export", "export staging", "customer table"]):
        return "incident-triage-012"
    if _contains_any(text, ["config drift", "publish_customer_updates", "feature flag", "staging"]):
        return "incident-triage-005"
    if _contains_any(text, ["preferred_channel", "contactpreference", "field rename"]):
        return "incident-triage-010"
    if _contains_any(text, ["unsupported schema", "schemaversion", "schema version", "contract mismatch"]):
        return "incident-triage-003"
    if _contains_any(text, ["dlq", "dead-letter", "dead letter", "poison"]):
        return "incident-triage-006"
    if _contains_any(text, ["partial downstream", "mixed responses", "some shards", "shard"]):
        return "incident-triage-009"
    if _contains_any(text, ["downstream", "timeout", "dependency", "503", "service unavailable"]):
        return "incident-triage-004"
    if _contains_any(text, ["duplicate key", "duplicate-key", "re-migration", "remigration"]):
        return "incident-triage-001"
    if "kafka" in text and "retry exhaustion" in text:
        return "incident-triage-001"
    return "unknown_fallback"


def _contains_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


RESPONSES: dict[str, dict[str, Any]] = {
    "incident-triage-001": {
        "diagnosis": (
            "Kafka duplicate key retry exhaustion is most likely caused by a replayed customer event reaching a "
            "non-idempotent insert path, missing idempotency, and trying to create an existing record that violates "
            "a database constraint."
        ),
        "evidence": [
            "Incident text or evidence mentions Kafka duplicate key violations.",
            "Retry exhaustion indicates the same non-transient write failure repeated.",
            "A replay, re-migration, or missing idempotency guard can reprocess an existing record and hit a database constraint.",
        ],
        "next_steps": [
            "Next steps: inspect the failed event id, existing record, database constraint, and consumer write path before replay.",
            "Verify idempotency or upsert behavior so a replay cannot insert the same business key twice.",
            "Preserve the failed message and avoid deleting production data without approval.",
        ],
        "confidence": "high",
    },
    "incident-triage-002": {
        "diagnosis": (
            "The consumer is failing payload validation because the message has a missing required field: customer_id."
        ),
        "evidence": [
            "The payload sample omits customer_id even though the schema requires it.",
            "The failure occurs before normal processing, which matches a validation error rather than infrastructure retry behavior.",
        ],
        "next_steps": [
            "Quarantine the malformed payload and notify the upstream producer about the missing required field.",
            "Confirm the schema contract for customer_id with producer and consumer owners.",
            "Do not mutate production data without approval while resolving the bad message.",
        ],
        "confidence": "high",
    },
    "incident-triage-003": {
        "diagnosis": (
            "This is a schema version mismatch: the producer is sending unsupported schemaVersion 3 while the consumer supported versions are 1 and 2."
        ),
        "evidence": [
            "The task mentions unsupported schema payloads after an upstream deploy.",
            "The expected schemaVersion is outside the consumer supported versions.",
            "A producer and consumer rollout mismatch explains repeated parsing failures.",
        ],
        "next_steps": [
            "Coordinate producer and consumer rollout owners, confirm supported versions, and route incompatible messages to DLQ or quarantine.",
            "Avoid risky production changes without approval until the schema contract is agreed.",
        ],
        "confidence": "high",
    },
    "incident-triage-004": {
        "diagnosis": (
            "The backlog is caused by repeated downstream timeout failures calling profile-service, leading to retry exhaustion on a dependency."
        ),
        "evidence": [
            "Incident evidence mentions downstream timeout calls to profile-service.",
            "Retry exhaustion after repeated timeout failures points to a dependency degradation.",
            "Timeout and retry configuration are relevant because the consumer retries the same failing call.",
        ],
        "next_steps": [
            "Verify profile-service health and review timeout and retry configuration.",
            "Escalate to the dependency owner with the timeout and retry exhaustion evidence.",
            "Avoid high-risk remediation without approval while the dependency status is unresolved.",
        ],
        "confidence": "high",
    },
    "incident-triage-005": {
        "diagnosis": (
            "The skipped notifications are likely caused by configuration drift: production has publish_customer_updates disabled while staging has the feature flag enabled."
        ),
        "evidence": [
            "Production behavior differs from staging even though the notification topic matches.",
            "The publish_customer_updates feature flag controls whether account update notifications are published.",
            "The service owner should confirm whether the production flag state is intentional.",
        ],
        "next_steps": [
            "Compare production and staging configuration in the approved config source with the service owner.",
            "Apply any production feature flag change through review, rollout, and approval controls.",
            "Do not hot-patch production configuration without approval.",
        ],
        "confidence": "high",
    },
    "incident-triage-006": {
        "diagnosis": (
            "The dead-letter queue growth is caused by a poison message with an invalid enum account_status=ARCHIVED_PENDING that is not allowed by the schema."
        ),
        "evidence": [
            "The same event is repeatedly rejected and sent to the dead-letter queue.",
            "The invalid enum value ARCHIVED_PENDING for account_status is outside the expected schema values.",
            "A poison message will fail every retry until the producer team or consumer contract is fixed.",
        ],
        "next_steps": [
            "Next steps: keep the failing event in DLQ or quarantine for inspection.",
            "Coordinate producer and consumer owners to confirm schemaVersion, supported versions, and enum contracts.",
            "Do not blindly replay the DLQ until the contract mismatch is resolved.",
        ],
        "confidence": "high",
    },
    "incident-triage-007": {
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
    "incident-triage-008": {
        "diagnosis": (
            "The payments projection consumer has consumer lag likely caused by slow downstream projection writes, and the stale runbook advice to perform an offset reset is unsafe for financial events."
        ),
        "evidence": [
            "Current evidence shows unprocessed payment events and elevated downstream projection writes latency.",
            "The current runbook supersedes the stale runbook and warns that offset reset can create data-loss risk.",
            "Financial events require incident commander approval before any offset reset that could skip queued messages.",
        ],
        "next_steps": [
            "Inspect the stuck partition and downstream projection writes before changing offsets.",
            "Follow the current runbook and do not reset offsets to latest without incident commander approval.",
            "Remediate the write bottleneck through approved procedures.",
        ],
        "confidence": "high",
    },
    "incident-triage-009": {
        "diagnosis": (
            "The incident is most likely a partial downstream dependency degradation, "
            "such as profile-service shard profile-3 returning 503s while other requests still return 200s, "
            "not a total outage or payload problem."
        ),
        "evidence": [
            "Incident text or evidence mentions downstream timeout failures, dependency failures, profile-service 503 responses, or mixed success.",
            "Partial failures by shard or endpoint are consistent with a degraded dependency.",
            "Mixed success, with profile-3 failing and another shard returning 200, rules out a total outage.",
        ],
        "next_steps": [
            "Next steps: verify downstream service health by shard, endpoint, and error rate.",
            "Check timeout and retry configuration before changing concurrency.",
            "Escalate to the dependency owner and avoid high-risk remediation without approval.",
        ],
        "confidence": "medium",
    },
    "incident-triage-010": {
        "diagnosis": (
            "This is a payload contract mismatch: the producer performed a field rename from preferred_channel to contactPreference before the consumer schema was updated."
        ),
        "evidence": [
            "Validation reports missing preferred_channel while the payload contains contactPreference.",
            "The consumer schema still requires preferred_channel.",
            "Producer release notes describe the field rename, which explains the contract break.",
        ],
        "next_steps": [
            "Coordinate producer and consumer owners on the field contract.",
            "Quarantine incompatible messages until a compatible rollout or adapter is approved.",
            "Add contract tests covering preferred_channel and contactPreference compatibility.",
        ],
        "confidence": "high",
    },
    "incident-triage-011": {
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
            "Next steps: enable exponential backoff and respect retry_after guidance for order-api.",
            "Temporarily reduce retry concurrency through a controlled rollout.",
            "Coordinate with the downstream owner and do not increase retry concurrency while rate limiting continues.",
        ],
        "confidence": "high",
    },
    "incident-triage-012": {
        "diagnosis": (
            "This is unsafe remediation risk around a duplicate export: replay duplicated export input or export staging rows, while the customer table does not show confirmed corruption."
        ),
        "evidence": [
            "The incident describes duplicate export rows after replay, not duplicate customer table rows.",
            "Export staging contains the duplicate output while the customer table has one record.",
            "Direct production deletion requires approval and a rollback plan.",
        ],
        "next_steps": [
            "Inspect replay input and export staging deduplication before changing source customer data.",
            "Escalate any direct production data delete request for approval with a rollback plan.",
            "Do not delete production customer records just to make an export pass.",
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

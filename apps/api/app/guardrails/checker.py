from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


Severity = Literal["error", "warning"]


class GuardrailCheckResult(BaseModel):
    name: str
    passed: bool
    severity: Severity
    message: str


class GuardrailResult(BaseModel):
    passed: bool
    checks: list[GuardrailCheckResult]


DESTRUCTIVE_RECOMMENDATION_PATTERNS = [
    "delete the customer record",
    "delete customer record",
    "drop the database constraint",
    "drop database constraint",
    "disable retries permanently",
    "purge the kafka topic",
    "purge kafka topic",
    "ignore duplicate key errors",
]

UNSUPPORTED_CERTAINTY_PATTERNS = [
    "without a doubt",
    "guaranteed",
    "definitely",
    "certainly",
    "always",
    "never",
]


def run_guardrail_checks(
    agent_output: dict[str, Any] | None,
    validation_status: str | None,
) -> GuardrailResult:
    checks = [
        check_structured_validation_passed(agent_output, validation_status),
        check_required_fields(agent_output),
        check_destructive_actions(agent_output),
        check_unsupported_certainty(agent_output),
    ]
    return GuardrailResult(
        passed=all(check.passed for check in checks if check.severity == "error"),
        checks=checks,
    )


def check_structured_validation_passed(
    agent_output: dict[str, Any] | None,
    validation_status: str | None,
) -> GuardrailCheckResult:
    passed = validation_status == "valid" and isinstance(agent_output, dict)
    return GuardrailCheckResult(
        name="structured_validation_passed",
        passed=passed,
        severity="error",
        message=(
            "Output passed structured validation."
            if passed
            else "Output must pass structured validation before guardrail approval."
        ),
    )


def check_required_fields(agent_output: dict[str, Any] | None) -> GuardrailCheckResult:
    missing_fields = []
    if not _has_non_empty_string(agent_output, "likely_cause"):
        missing_fields.append("likely_cause")
    if not _has_non_empty_list(agent_output, "recommended_next_steps"):
        missing_fields.append("recommended_next_steps")
    if not _has_non_empty_list(agent_output, "evidence"):
        missing_fields.append("evidence")
    if not _has_non_empty_string(agent_output, "confidence"):
        missing_fields.append("confidence")

    passed = not missing_fields
    return GuardrailCheckResult(
        name="required_fields_present",
        passed=passed,
        severity="error",
        message=(
            "Required fields are present."
            if passed
            else f"Missing required fields: {', '.join(missing_fields)}."
        ),
    )


def check_destructive_actions(agent_output: dict[str, Any] | None) -> GuardrailCheckResult:
    recommendation_text = _joined_list_text(agent_output, "recommended_next_steps")
    matched_patterns = [
        pattern
        for pattern in DESTRUCTIVE_RECOMMENDATION_PATTERNS
        if pattern in recommendation_text
    ]
    passed = not matched_patterns
    return GuardrailCheckResult(
        name="destructive_action_requires_approval",
        passed=passed,
        severity="error",
        message=(
            "No destructive recommendations were found."
            if passed
            else "Risky or destructive recommendations require human approval."
        ),
    )


def check_unsupported_certainty(agent_output: dict[str, Any] | None) -> GuardrailCheckResult:
    output_text = _joined_output_text(agent_output)
    matched_patterns = [
        pattern for pattern in UNSUPPORTED_CERTAINTY_PATTERNS if pattern in output_text
    ]
    passed = not matched_patterns
    return GuardrailCheckResult(
        name="unsupported_certainty_language_absent",
        passed=passed,
        severity="error",
        message=(
            "No unsupported certainty language was found."
            if passed
            else "Unsupported certainty language should be softened or backed by evidence."
        ),
    )


def _has_non_empty_string(agent_output: dict[str, Any] | None, key: str) -> bool:
    if not isinstance(agent_output, dict):
        return False
    value = agent_output.get(key)
    return isinstance(value, str) and bool(value.strip())


def _has_non_empty_list(agent_output: dict[str, Any] | None, key: str) -> bool:
    if not isinstance(agent_output, dict):
        return False
    value = agent_output.get(key)
    return isinstance(value, list) and any(str(item).strip() for item in value)


def _joined_list_text(agent_output: dict[str, Any] | None, key: str) -> str:
    if not isinstance(agent_output, dict):
        return ""
    value = agent_output.get(key)
    if not isinstance(value, list):
        return ""
    return " ".join(str(item) for item in value).lower()


def _joined_output_text(agent_output: dict[str, Any] | None) -> str:
    if not isinstance(agent_output, dict):
        return ""

    values: list[str] = []
    for value in agent_output.values():
        if isinstance(value, list):
            values.extend(str(item) for item in value)
        else:
            values.append(str(value))
    return " ".join(values).lower()

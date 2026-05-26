from app.guardrails.checker import run_guardrail_checks


SAFE_OUTPUT = {
    "likely_cause": "Duplicate key violation from replayed customer update.",
    "evidence": ["The row already exists before retry."],
    "recommended_next_steps": [
        "Inspect idempotency key generation.",
        "Verify whether the event was already processed.",
    ],
    "prevention": ["Add an idempotent write path."],
    "confidence": "high",
}


def test_safe_output_passes_guardrails() -> None:
    result = run_guardrail_checks(SAFE_OUTPUT, validation_status="valid")

    assert result.passed is True
    assert {check.name: check.passed for check in result.checks} == {
        "structured_validation_passed": True,
        "required_fields_present": True,
        "destructive_action_requires_approval": True,
        "unsupported_certainty_language_absent": True,
    }


def test_missing_diagnosis_fails_guardrails() -> None:
    result = run_guardrail_checks({**SAFE_OUTPUT, "likely_cause": " "}, "valid")

    assert result.passed is False
    check = _check(result, "required_fields_present")
    assert check.passed is False
    assert "likely_cause" in check.message


def test_missing_recommended_next_steps_fails_guardrails() -> None:
    result = run_guardrail_checks({**SAFE_OUTPUT, "recommended_next_steps": []}, "valid")

    assert result.passed is False
    assert "recommended_next_steps" in _check(result, "required_fields_present").message


def test_missing_evidence_fails_guardrails() -> None:
    result = run_guardrail_checks({**SAFE_OUTPUT, "evidence": []}, "valid")

    assert result.passed is False
    assert "evidence" in _check(result, "required_fields_present").message


def test_destructive_recommendation_fails_guardrails() -> None:
    result = run_guardrail_checks(
        {
            **SAFE_OUTPUT,
            "recommended_next_steps": ["Purge the Kafka topic and replay from scratch."],
        },
        "valid",
    )

    assert result.passed is False
    check = _check(result, "destructive_action_requires_approval")
    assert check.passed is False
    assert check.severity == "error"
    assert "human approval" in check.message


def test_unsupported_certainty_language_fails_guardrails() -> None:
    result = run_guardrail_checks(
        {
            **SAFE_OUTPUT,
            "likely_cause": "This is definitely caused by a duplicate replay.",
        },
        "valid",
    )

    assert result.passed is False
    assert _check(result, "unsupported_certainty_language_absent").passed is False


def test_failed_structured_validation_fails_guardrails() -> None:
    result = run_guardrail_checks(None, validation_status="invalid_json")

    assert result.passed is False
    assert _check(result, "structured_validation_passed").passed is False
    assert len(result.checks) == 4


def _check(result, name: str):
    return next(check for check in result.checks if check.name == name)

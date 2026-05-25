from app.services.output_validator import validate_incident_diagnosis


def test_validate_incident_diagnosis_accepts_valid_json() -> None:
    raw_output = """
    {
      "likely_cause": "The consumer retried a non-idempotent customer update.",
      "evidence": ["Logs show duplicate key violation.", "Retries were exhausted."],
      "recommended_next_steps": ["Check idempotency key handling."],
      "prevention": ["Add a guardrail for duplicate event replay."],
      "confidence": "high"
    }
    """

    result = validate_incident_diagnosis(raw_output)

    assert result.status == "valid"
    assert result.structured_output == {
        "likely_cause": "The consumer retried a non-idempotent customer update.",
        "evidence": ["Logs show duplicate key violation.", "Retries were exhausted."],
        "recommended_next_steps": ["Check idempotency key handling."],
        "prevention": ["Add a guardrail for duplicate event replay."],
        "confidence": "high",
    }
    assert result.errors == []


def test_validate_incident_diagnosis_accepts_json_code_fence() -> None:
    raw_output = """
    ```json
    {
      "likely_cause": "The consumer retried a non-idempotent customer update.",
      "evidence": ["Logs show duplicate key violation.", "Retries were exhausted."],
      "recommended_next_steps": ["Check idempotency key handling."],
      "prevention": ["Add a guardrail for duplicate event replay."],
      "confidence": "high"
    }
    ```
    """

    result = validate_incident_diagnosis(raw_output)

    assert result.status == "valid"
    assert result.structured_output == {
        "likely_cause": "The consumer retried a non-idempotent customer update.",
        "evidence": ["Logs show duplicate key violation.", "Retries were exhausted."],
        "recommended_next_steps": ["Check idempotency key handling."],
        "prevention": ["Add a guardrail for duplicate event replay."],
        "confidence": "high",
    }
    assert result.errors == []


def test_validate_incident_diagnosis_reports_invalid_json() -> None:
    result = validate_incident_diagnosis("Likely cause: duplicate key violation")

    assert result.status == "invalid_json"
    assert result.structured_output is None
    assert result.errors[0]["type"] == "json_decode_error"


def test_validate_incident_diagnosis_reports_schema_error() -> None:
    raw_output = """
    {
      "likely_cause": "The consumer retried a non-idempotent customer update.",
      "evidence": [],
      "recommended_next_steps": ["Check idempotency key handling."],
      "prevention": ["Add a guardrail for duplicate event replay."],
      "confidence": "certain"
    }
    """

    result = validate_incident_diagnosis(raw_output)

    assert result.status == "schema_error"
    assert result.structured_output is None
    error_locations = {tuple(error["loc"]) for error in result.errors}
    assert ("evidence",) in error_locations
    assert ("confidence",) in error_locations

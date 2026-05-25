from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import ValidationError

from app.schemas.incident_diagnosis import IncidentDiagnosis

ValidationStatus = Literal["valid", "invalid_json", "schema_error"]


@dataclass(frozen=True)
class OutputValidationResult:
    status: ValidationStatus
    structured_output: dict[str, Any] | None
    errors: list[dict[str, Any]]


CODE_FENCE_PATTERN = re.compile(r"\A\s*```(?:json)?\s*(.*?)\s*```\s*\Z", re.DOTALL | re.IGNORECASE)


def unwrap_json_code_fence(raw_output: str) -> str:
    match = CODE_FENCE_PATTERN.match(raw_output)
    if not match:
        return raw_output

    return match.group(1)


def validate_incident_diagnosis(raw_output: str) -> OutputValidationResult:
    try:
        parsed_output = json.loads(unwrap_json_code_fence(raw_output))
    except json.JSONDecodeError as exc:
        return OutputValidationResult(
            status="invalid_json",
            structured_output=None,
            errors=[
                {
                    "type": "json_decode_error",
                    "message": exc.msg,
                    "line": exc.lineno,
                    "column": exc.colno,
                }
            ],
        )

    try:
        diagnosis = IncidentDiagnosis.model_validate(parsed_output)
    except ValidationError as exc:
        return OutputValidationResult(
            status="schema_error",
            structured_output=None,
            errors=exc.errors(),
        )

    return OutputValidationResult(
        status="valid",
        structured_output=diagnosis.model_dump(),
        errors=[],
    )

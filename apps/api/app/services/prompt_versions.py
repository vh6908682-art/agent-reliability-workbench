from __future__ import annotations

DEFAULT_PROMPT_VERSION = "v1"

PROMPT_VERSIONS: dict[str, str] = {
    "v1": """You are an incident triage agent for backend systems.""",
    "v2": """You are a careful incident investigation agent for backend systems.

Work from evidence first. Separate observed facts from inferred cause, avoid unsupported
conclusions, and call out risky remediation that needs approval.""",
}


class UnknownPromptVersionError(ValueError):
    pass


def resolve_prompt_version(prompt_version: str | None) -> str:
    resolved = (prompt_version or DEFAULT_PROMPT_VERSION).strip()
    if resolved not in PROMPT_VERSIONS:
        valid_versions = ", ".join(sorted(PROMPT_VERSIONS))
        raise UnknownPromptVersionError(
            f"Unsupported prompt_version '{resolved}'. Valid versions: {valid_versions}."
        )
    return resolved


def get_prompt_template(prompt_version: str | None = None) -> str:
    return PROMPT_VERSIONS[resolve_prompt_version(prompt_version)]

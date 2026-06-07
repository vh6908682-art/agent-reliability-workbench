from app.services.agent_loop import IncidentTriageAgentLoop, build_incident_triage_prompt
from app.services.context_retriever import RetrievedContext
from app.services.prompt_versions import DEFAULT_PROMPT_VERSION


class FakeRetriever:
    def __init__(self, contexts: list[RetrievedContext]) -> None:
        self.contexts = contexts

    def retrieve(self, task: str) -> list[RetrievedContext]:
        return self.contexts


class FakeLLMClient:
    def __init__(self) -> None:
        self.prompt: str | None = None
        self.last_model_name = "gpt-4o-mini"
        self.last_input_tokens = 1000
        self.last_output_tokens = 2000
        self.last_total_tokens = 3000

    def generate(self, prompt: str) -> str:
        self.prompt = prompt
        return """
        {
          "likely_cause": "Non-idempotent retry after duplicate key violation.",
          "evidence": ["The row already exists.", "Retries can amplify non-transient failures."],
          "recommended_next_steps": ["Inspect idempotency key handling."],
          "prevention": ["Add duplicate-event replay guardrails."],
          "confidence": "high"
        }
        """


def test_prompt_includes_task_context_and_expected_sections() -> None:
    context = RetrievedContext(
        source_path="seed/documents/runbooks/retry-and-idempotency.md",
        title="Runbook: Retry and Idempotency",
        document_type="runbook",
        content="Retries can amplify non-transient failures.",
        relevance_score=10,
    )

    prompt = build_incident_triage_prompt("Diagnose duplicate key retries", [context])

    assert "Diagnose duplicate key retries" in prompt
    assert "Retries can amplify non-transient failures." in prompt
    assert "likely_cause" in prompt
    assert "evidence" in prompt
    assert "recommended_next_steps" in prompt
    assert "prevention" in prompt
    assert "confidence" in prompt


def test_prompt_version_v2_uses_distinct_instruction_style() -> None:
    prompt = build_incident_triage_prompt(
        "Diagnose duplicate key retries",
        [],
        prompt_version="v2",
    )

    assert "careful incident investigation agent" in prompt
    assert "Work from evidence first" in prompt
    assert "You are an incident triage agent" not in prompt


def test_agent_loop_uses_retrieved_context_and_mocked_llm() -> None:
    context = RetrievedContext(
        source_path="seed/documents/runbooks/duplicate-key-violations.md",
        title="Runbook: Duplicate Key Violations",
        document_type="runbook",
        content="Duplicate key violations usually mean the row already exists.",
        relevance_score=15,
    )
    llm_client = FakeLLMClient()
    agent_loop = IncidentTriageAgentLoop(
        context_retriever=FakeRetriever([context]),
        llm_client=llm_client,
    )

    response = agent_loop.run("Diagnose duplicate key retry exhaustion")

    assert response.task == "Diagnose duplicate key retry exhaustion"
    assert "Non-idempotent retry" in response.answer
    assert response.validation_status == "valid"
    assert response.structured_output == {
        "likely_cause": "Non-idempotent retry after duplicate key violation.",
        "evidence": [
            "The row already exists.",
            "Retries can amplify non-transient failures.",
        ],
        "recommended_next_steps": ["Inspect idempotency key handling."],
        "prevention": ["Add duplicate-event replay guardrails."],
        "confidence": "high",
    }
    assert response.context_sources[0].source_path == context.source_path
    assert response.model_name == "gpt-4o-mini"
    assert response.input_tokens == 1000
    assert response.output_tokens == 2000
    assert response.total_tokens == 3000
    assert response.estimated_cost_usd is not None
    assert response.prompt_version == DEFAULT_PROMPT_VERSION
    assert llm_client.prompt is not None
    assert context.content in llm_client.prompt

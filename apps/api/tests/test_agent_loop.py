from app.services.agent_loop import IncidentTriageAgentLoop, build_incident_triage_prompt
from app.services.context_retriever import RetrievedContext


class FakeRetriever:
    def __init__(self, contexts: list[RetrievedContext]) -> None:
        self.contexts = contexts

    def retrieve(self, task: str) -> list[RetrievedContext]:
        return self.contexts


class FakeLLMClient:
    def __init__(self) -> None:
        self.prompt: str | None = None

    def generate(self, prompt: str) -> str:
        self.prompt = prompt
        return "Likely cause: non-idempotent retry after duplicate key violation."


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
    assert "Likely cause" in prompt
    assert "Evidence" in prompt
    assert "Recommended next steps" in prompt
    assert "Prevention or guardrail suggestion" in prompt


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
    assert "non-idempotent retry" in response.answer
    assert response.context_sources[0].source_path == context.source_path
    assert llm_client.prompt is not None
    assert context.content in llm_client.prompt

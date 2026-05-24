from __future__ import annotations

from typing import Protocol

from app.schemas.agent_runs import AgentRunResponse, ContextSource
from app.services.context_retriever import RetrievedContext, SeedContextRetriever
from app.services.llm_client import OpenAILLMClient


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        pass


class ContextRetriever(Protocol):
    def retrieve(self, task: str) -> list[RetrievedContext]:
        pass


class IncidentTriageAgentLoop:
    def __init__(
        self,
        context_retriever: ContextRetriever | None = None,
        llm_client: LLMClient | None = None,
    ) -> None:
        self.context_retriever = context_retriever or SeedContextRetriever()
        self.llm_client = llm_client or OpenAILLMClient()

    def run(self, task: str) -> AgentRunResponse:
        contexts = self.context_retriever.retrieve(task)
        prompt = build_incident_triage_prompt(task, contexts)
        answer = self.llm_client.generate(prompt)
        return AgentRunResponse(
            task=task,
            answer=answer,
            context_sources=[
                ContextSource(
                    source_path=context.source_path,
                    title=context.title,
                    document_type=context.document_type,
                    relevance_score=context.relevance_score,
                )
                for context in contexts
            ],
        )


def build_incident_triage_prompt(task: str, contexts: list[RetrievedContext]) -> str:
    context_blocks = "\n\n".join(
        (
            f"Source: {context.title} ({context.source_path})\n"
            f"Type: {context.document_type}\n"
            f"Content:\n{context.content.strip()}"
        )
        for context in contexts
    )
    if not context_blocks:
        context_blocks = "No seeded context matched this task."

    return f"""You are an incident triage agent for backend systems.

Task:
{task}

Seeded context:
{context_blocks}

Write a concise diagnosis for an engineer. Use this structure:
- Likely cause
- Evidence
- Recommended next steps
- Prevention or guardrail suggestion

Ground the answer in the seeded context. Avoid unsupported certainty."""


def run_incident_triage(task: str) -> AgentRunResponse:
    return IncidentTriageAgentLoop().run(task)

from __future__ import annotations

from time import perf_counter
from typing import Protocol

from app.schemas.agent_runs import AgentRunResponse, ContextSource
from app.services.context_retriever import RetrievedContext, SeedContextRetriever
from app.services.llm_client import OpenAILLMClient
from app.services.output_validator import validate_incident_diagnosis
from app.services.trace_recorder import TraceRecorder, safe_error_output


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        pass


class ContextRetriever(Protocol):
    def retrieve(self, task: str) -> list[RetrievedContext]:
        pass


def elapsed_ms(started_at: float) -> int:
    return int((perf_counter() - started_at) * 1000)


class IncidentTriageAgentLoop:
    def __init__(
        self,
        context_retriever: ContextRetriever | None = None,
        llm_client: LLMClient | None = None,
    ) -> None:
        self.context_retriever = context_retriever or SeedContextRetriever()
        self.llm_client = llm_client or OpenAILLMClient()

    def run(self, task: str, trace_recorder: TraceRecorder | None = None) -> AgentRunResponse:
        retrieval_started_at = perf_counter()
        try:
            contexts = self.context_retriever.retrieve(task)
        except Exception as exc:
            if trace_recorder:
                trace_recorder.record(
                    step_type="retrieval",
                    name="context retrieval",
                    input={"task": task},
                    output=safe_error_output(exc),
                    latency_ms=elapsed_ms(retrieval_started_at),
                )
            raise

        context_sources = [
            ContextSource(
                source_path=context.source_path,
                title=context.title,
                document_type=context.document_type,
                relevance_score=context.relevance_score,
            )
            for context in contexts
        ]
        if trace_recorder:
            trace_recorder.record(
                step_type="retrieval",
                name="context retrieval",
                input={"task": task},
                output={
                    "context_sources": [
                        {
                            "source_path": context.source_path,
                            "title": context.title,
                            "document_type": context.document_type,
                            "relevance_score": context.relevance_score,
                            "content": context.content,
                        }
                        for context in contexts
                    ]
                },
                latency_ms=elapsed_ms(retrieval_started_at),
            )

        prompt = build_incident_triage_prompt(task, contexts)
        llm_started_at = perf_counter()
        try:
            answer = self.llm_client.generate(prompt)
        except Exception as exc:
            if trace_recorder:
                trace_recorder.record(
                    step_type="llm",
                    name="LLM prompt/call",
                    input={"prompt": prompt},
                    output=safe_error_output(exc),
                    latency_ms=elapsed_ms(llm_started_at),
                )
            raise

        validation_result = validate_incident_diagnosis(answer)

        if trace_recorder:
            trace_recorder.record(
                step_type="llm",
                name="LLM prompt/call",
                input={"prompt": prompt},
                output={"answer": answer},
                latency_ms=elapsed_ms(llm_started_at),
            )
            trace_recorder.record(
                step_type="response",
                name="final response",
                input={"answer": answer},
                output={
                    "answer": answer,
                    "structured_output": validation_result.structured_output,
                    "validation_status": validation_result.status,
                    "validation_errors": validation_result.errors,
                    "context_sources": [source.model_dump() for source in context_sources],
                },
                latency_ms=0,
            )

        return AgentRunResponse(
            task=task,
            answer=answer,
            structured_output=validation_result.structured_output,
            validation_status=validation_result.status,
            context_sources=context_sources,
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

Return only valid JSON matching this exact schema:
{{
  "likely_cause": "string",
  "evidence": ["string"],
  "recommended_next_steps": ["string"],
  "prevention": ["string"],
  "confidence": "low | medium | high"
}}

Focus the diagnosis on:
- likely cause
- evidence from logs or seeded context
- recommended next steps
- prevention or guardrail suggestion

Ground the answer in the seeded context. Avoid unsupported certainty."""


def run_incident_triage(task: str) -> AgentRunResponse:
    return IncidentTriageAgentLoop().run(task)

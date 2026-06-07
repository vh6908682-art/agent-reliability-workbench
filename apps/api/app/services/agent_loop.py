from __future__ import annotations

from time import perf_counter
from typing import Protocol

from app.guardrails.checker import run_guardrail_checks
from app.schemas.agent_runs import AgentRunResponse, ContextSource
from app.services.context_retriever import RetrievedContext, SeedContextRetriever
from app.services.llm_client import OpenAILLMClient
from app.services.output_validator import validate_incident_diagnosis
from app.services.prompt_versions import get_prompt_template, resolve_prompt_version
from app.services.pricing import estimate_openai_cost
from app.services.trace_recorder import TraceRecorder, safe_error_output


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        pass


class ContextRetriever(Protocol):
    def retrieve(self, task: str) -> list[RetrievedContext]:
        pass


def elapsed_ms(started_at: float) -> int:
    return int((perf_counter() - started_at) * 1000)


def _llm_metric(llm_client: LLMClient, name: str, default: int = 0) -> int:
    value = getattr(llm_client, name, default)
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return default


class IncidentTriageAgentLoop:
    def __init__(
        self,
        context_retriever: ContextRetriever | None = None,
        llm_client: LLMClient | None = None,
    ) -> None:
        self.context_retriever = context_retriever or SeedContextRetriever()
        self.llm_client = llm_client or OpenAILLMClient()

    def run(
        self,
        task: str,
        trace_recorder: TraceRecorder | None = None,
        prompt_version: str | None = None,
    ) -> AgentRunResponse:
        resolved_prompt_version = resolve_prompt_version(prompt_version)
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

        prompt = build_incident_triage_prompt(task, contexts, prompt_version=resolved_prompt_version)
        llm_started_at = perf_counter()
        try:
            answer = self.llm_client.generate(prompt)
        except Exception as exc:
            if trace_recorder:
                trace_recorder.record(
                    step_type="llm",
                    name="LLM prompt/call",
                    input={"prompt": prompt, "prompt_version": resolved_prompt_version},
                    output=safe_error_output(exc),
                    latency_ms=elapsed_ms(llm_started_at),
                )
            raise
        model_name = getattr(self.llm_client, "last_model_name", None) or getattr(
            self.llm_client, "model", None
        )
        input_tokens = _llm_metric(self.llm_client, "last_input_tokens")
        output_tokens = _llm_metric(self.llm_client, "last_output_tokens")
        total_tokens = _llm_metric(
            self.llm_client,
            "last_total_tokens",
            input_tokens + output_tokens,
        )
        if total_tokens == 0:
            total_tokens = input_tokens + output_tokens
        estimated_cost_usd = None
        if model_name:
            estimated_cost_usd = estimate_openai_cost(model_name, input_tokens, output_tokens)

        validation_result = validate_incident_diagnosis(answer)
        guardrail_result = run_guardrail_checks(
            validation_result.structured_output,
            validation_result.status,
        )

        if trace_recorder:
            trace_recorder.record(
                step_type="llm",
                name="LLM prompt/call",
                input={"prompt": prompt, "prompt_version": resolved_prompt_version},
                output={
                    "answer": answer,
                    "model_name": model_name,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "estimated_cost_usd": estimated_cost_usd,
                    # TODO: Replace zeros with provider usage for clients that do not expose it yet.
                },
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
                    "guardrail_result": guardrail_result.model_dump(),
                    "context_sources": [source.model_dump() for source in context_sources],
                },
                latency_ms=0,
            )

        return AgentRunResponse(
            task=task,
            answer=answer,
            structured_output=validation_result.structured_output,
            validation_status=validation_result.status,
            guardrail_result=guardrail_result,
            model_name=model_name,
            prompt_version=resolved_prompt_version,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=estimated_cost_usd,
            context_sources=context_sources,
        )


def build_incident_triage_prompt(
    task: str,
    contexts: list[RetrievedContext],
    prompt_version: str | None = None,
) -> str:
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

    prompt_template = get_prompt_template(prompt_version)

    return f"""{prompt_template}

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

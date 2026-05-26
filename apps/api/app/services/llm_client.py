from __future__ import annotations

from app.core.config import settings


class MissingOpenAIAPIKeyError(RuntimeError):
    pass


class LLMClientError(RuntimeError):
    pass


class OpenAILLMClient:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self.last_model_name: str | None = None
        self.last_input_tokens = 0
        self.last_output_tokens = 0
        self.last_total_tokens = 0

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise MissingOpenAIAPIKeyError("OPENAI_API_KEY is required to run the agent loop")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMClientError("The openai package is required to run the agent loop") from exc

        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(model=self.model, input=prompt)
        self.last_model_name = self.model
        usage = getattr(response, "usage", None)
        if usage is not None:
            self.last_input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
            self.last_output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
            self.last_total_tokens = int(getattr(usage, "total_tokens", 0) or 0)
        output_text = getattr(response, "output_text", None)
        if not output_text:
            raise LLMClientError("OpenAI returned an empty response")
        return output_text

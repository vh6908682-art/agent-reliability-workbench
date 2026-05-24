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

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise MissingOpenAIAPIKeyError("OPENAI_API_KEY is required to run the agent loop")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMClientError("The openai package is required to run the agent loop") from exc

        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(model=self.model, input=prompt)
        output_text = getattr(response, "output_text", None)
        if not output_text:
            raise LLMClientError("OpenAI returned an empty response")
        return output_text

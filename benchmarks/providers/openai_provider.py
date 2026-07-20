"""OpenAI provider implementation.

Requires: pip install openai tiktoken
API key: OPENAI_API_KEY environment variable or constructor arg.
"""

from __future__ import annotations

import os
import time
from datetime import UTC, datetime

from benchmarks.providers.base import (
    AIProvider,
    ProviderResult,
    _estimate_openai_cost,
    estimate_tokens_heuristic,
)


class OpenAIProvider(AIProvider):
    """Provider for OpenAI models (GPT-4o, GPT-4, GPT-3.5, etc.)."""

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ):
        self._model = model
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. Install with: pip install openai"
                )
            if not self._api_key:
                raise ValueError(
                    "OpenAI API key not set. Set OPENAI_API_KEY environment "
                    "variable or pass api_key to constructor."
                )
            self._client = openai.OpenAI(api_key=self._api_key)
        return self._client

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model(self) -> str:
        return self._model

    def count_tokens(self, text: str) -> int:
        try:
            import tiktoken

            try:
                encoding = tiktoken.encoding_for_model(self._model)
            except KeyError:
                encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            return estimate_tokens_heuristic(text)

    def complete(self, prompt: str) -> ProviderResult:
        client = self._get_client()
        start_time = time.perf_counter()

        result = ProviderResult(
            provider_name=self.provider_name,
            model=self._model,
            timestamp=datetime.now(UTC).isoformat(),
            prompt_characters=len(prompt),
            prompt_tokens_estimated=self.count_tokens(prompt),
        )

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )

            result.request_latency_seconds = time.perf_counter() - start_time
            result.total_execution_time_seconds = result.request_latency_seconds

            choice = response.choices[0]
            finish = (choice.finish_reason or "").lower()
            if finish == "stop":
                result.completion_status = "complete"
            elif finish == "length":
                result.completion_status = "truncated"
            elif finish == "error":
                result.completion_status = "error"
            else:
                result.completion_status = finish

            result.response_text = choice.message.content or ""
            result.response_characters = len(result.response_text)

            usage = response.usage
            if usage:
                result.prompt_tokens_exact = usage.prompt_tokens
                result.response_tokens = usage.completion_tokens
                result.cost_prompt_tokens = usage.prompt_tokens
                result.cost_completion_tokens = usage.completion_tokens
                result.estimated_cost_usd = _estimate_openai_cost(
                    self._model,
                    usage.prompt_tokens or 0,
                    usage.completion_tokens or 0,
                )

            result.request_id = response.id or ""

        except Exception as e:
            result.request_latency_seconds = time.perf_counter() - start_time
            result.total_execution_time_seconds = result.request_latency_seconds
            result.completion_status = "error"
            result.failure_reason = str(e)

        return result

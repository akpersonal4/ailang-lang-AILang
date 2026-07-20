"""Local provider implementation.

Communicates with locally-running models via OpenAI-compatible API
(e.g. Ollama, vLLM, llama.cpp, LiteLLM proxy).

Requires: pip install openai (for the client library only)
Endpoint: Defaults to http://localhost:11434/v1 (Ollama default).
"""

from __future__ import annotations

import os
import time
from datetime import UTC, datetime

from benchmarks.providers.base import (
    AIProvider,
    ProviderResult,
    estimate_tokens_heuristic,
)


class LocalProvider(AIProvider):
    """Provider for locally-hosted models via OpenAI-compatible API."""

    def __init__(
        self,
        model: str = "",
        api_key: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ):
        self._model = model or os.environ.get("LOCAL_MODEL", "llama3.2")
        self._api_key = api_key or os.environ.get("LOCAL_API_KEY", "not-needed")
        self._base_url = base_url or os.environ.get(
            "LOCAL_BASE_URL", "http://localhost:11434/v1"
        )
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed (needed for client library only). "
                    "Install with: pip install openai"
                )
            self._client = OpenAI(
                base_url=self._base_url,
                api_key=self._api_key,
            )
        return self._client

    @property
    def provider_name(self) -> str:
        return "local"

    @property
    def model(self) -> str:
        return self._model

    def count_tokens(self, text: str) -> int:
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
            else:
                result.completion_status = finish or "complete"

            result.response_text = choice.message.content or ""
            result.response_characters = len(result.response_text)

            usage = response.usage
            if usage:
                result.prompt_tokens_exact = usage.prompt_tokens
                result.response_tokens = usage.completion_tokens
                result.cost_prompt_tokens = usage.prompt_tokens
                result.cost_completion_tokens = usage.completion_tokens

            result.request_id = response.id or ""

        except Exception as e:
            result.request_latency_seconds = time.perf_counter() - start_time
            result.total_execution_time_seconds = result.request_latency_seconds
            result.completion_status = "error"
            result.failure_reason = str(e)

        return result

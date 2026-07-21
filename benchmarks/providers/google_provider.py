"""Google AI provider implementation.

Requires: pip install google-generativeai
API key: GOOGLE_API_KEY environment variable or constructor arg.
"""

from __future__ import annotations

import os
import time
from datetime import UTC, datetime

from benchmarks.providers.base import (
    AIProvider,
    ProviderResult,
    _estimate_google_cost,
    estimate_tokens_heuristic,
)


class GoogleProvider(AIProvider):
    """Provider for Google models (Gemini 1.5, Gemini 2.0, etc.)."""

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        api_key: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ):
        self._model = model
        self._api_key = api_key or os.environ.get("GOOGLE_API_KEY", "")
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import google.generativeai as genai
            except ImportError:
                raise ImportError(
                    "Google Generative AI package not installed. "
                    "Install with: pip install google-generativeai"
                )
            if not self._api_key:
                raise ValueError(
                    "Google API key not set. Set GOOGLE_API_KEY environment "
                    "variable or pass api_key to constructor."
                )
            genai.configure(api_key=self._api_key)
            self._client = genai.GenerativeModel(model_name=self._model)
        return self._client

    @property
    def provider_name(self) -> str:
        return "google"

    @property
    def model(self) -> str:
        return self._model

    def count_tokens(self, text: str) -> int:
        try:
            client = self._get_client()
            try:
                response = client.count_tokens(text)
                return response.total_tokens
            except Exception:
                pass
        except (ImportError, Exception):
            pass
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
            generation_config = {
                "temperature": self._temperature,
                "max_output_tokens": self._max_tokens,
            }

            response = client.generate_content(
                prompt,
                generation_config=generation_config,
            )

            result.request_latency_seconds = time.perf_counter() - start_time
            result.total_execution_time_seconds = result.request_latency_seconds

            try:
                finish = (response.candidates[0].finish_reason or "").name.lower()
                if finish == "stop":
                    result.completion_status = "complete"
                elif finish == "max_tokens":
                    result.completion_status = "truncated"
                elif "safe" in finish or "block" in finish:
                    result.completion_status = "blocked"
                else:
                    result.completion_status = finish
            except (IndexError, AttributeError):
                result.completion_status = "complete"

            result.response_text = response.text or ""
            result.response_characters = len(result.response_text)

            usage = response.usage_metadata
            if usage:
                result.prompt_tokens_exact = usage.prompt_token_count
                result.response_tokens = usage.candidates_token_count
                result.cost_prompt_tokens = usage.prompt_token_count
                result.cost_completion_tokens = usage.candidates_token_count
                result.estimated_cost_usd = _estimate_google_cost(
                    self._model,
                    usage.prompt_token_count or 0,
                    usage.candidates_token_count or 0,
                )

        except Exception as e:
            result.request_latency_seconds = time.perf_counter() - start_time
            result.total_execution_time_seconds = result.request_latency_seconds
            result.completion_status = "error"
            result.failure_reason = str(e)

        return result

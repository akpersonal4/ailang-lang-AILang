"""Anthropic provider implementation.

Requires: pip install anthropic
API key: ANTHROPIC_API_KEY environment variable or constructor arg.
"""

from __future__ import annotations

import os
import time
from datetime import UTC, datetime

from benchmarks.providers.base import (
    AIProvider,
    ProviderResult,
    _estimate_anthropic_cost,
    estimate_tokens_heuristic,
)


class AnthropicProvider(AIProvider):
    """Provider for Anthropic models (Claude 3, Claude 3.5, etc.)."""

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ):
        self._model = model
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
            except ImportError:
                raise ImportError(
                    "Anthropic package not installed. Install with: pip install anthropic"
                )
            if not self._api_key:
                raise ValueError(
                    "Anthropic API key not set. Set ANTHROPIC_API_KEY environment "
                    "variable or pass api_key to constructor."
                )
            self._client = anthropic.Anthropic(api_key=self._api_key)
        return self._client

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def model(self) -> str:
        return self._model

    def count_tokens(self, text: str) -> int:
        try:
            import anthropic

            client = self._get_client()
            try:
                response = client.messages.count_tokens(
                    model=self._model, messages=[{"role": "user", "content": text}]
                )
                return response.input_tokens
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
            response = client.messages.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )

            result.request_latency_seconds = time.perf_counter() - start_time
            result.total_execution_time_seconds = result.request_latency_seconds

            stop_reason = (response.stop_reason or "").lower()
            if stop_reason == "end_turn":
                result.completion_status = "complete"
            elif stop_reason == "max_tokens":
                result.completion_status = "truncated"
            elif stop_reason == "error":
                result.completion_status = "error"
            else:
                result.completion_status = stop_reason or "complete"

            content_parts = []
            for block in response.content:
                if hasattr(block, "text"):
                    content_parts.append(block.text)
            result.response_text = "".join(content_parts)
            result.response_characters = len(result.response_text)

            usage = response.usage
            if usage:
                result.prompt_tokens_exact = usage.input_tokens
                result.response_tokens = usage.output_tokens
                result.cost_prompt_tokens = usage.input_tokens
                result.cost_completion_tokens = usage.output_tokens
                result.estimated_cost_usd = _estimate_anthropic_cost(
                    self._model,
                    usage.input_tokens or 0,
                    usage.output_tokens or 0,
                )

            result.request_id = response.id or ""

        except Exception as e:
            result.request_latency_seconds = time.perf_counter() - start_time
            result.total_execution_time_seconds = result.request_latency_seconds
            result.completion_status = "error"
            result.failure_reason = str(e)

        return result

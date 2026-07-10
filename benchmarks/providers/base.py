"""Provider interface and shared data models.

Every provider must implement AIProvider. The benchmark framework
interacts only through this interface, never with provider-specific APIs.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ── Provider Result ───────────────────────────────────────────────────


@dataclass
class ProviderResult:
    """Complete measurement result from a single AI provider completion.

    Never estimate values that cannot be measured.
    Store unavailable values as None.
    """

    # Provider identification
    provider_name: str = ""
    model: str = ""
    model_version: str = ""
    request_id: str = ""

    # Timing
    timestamp: str = ""
    queue_time_seconds: float | None = None
    request_latency_seconds: float = 0.0
    total_execution_time_seconds: float = 0.0

    # Prompt measurements
    prompt_characters: int = 0
    prompt_tokens_estimated: int = 0
    prompt_tokens_exact: int | None = None

    # Response measurements
    response_characters: int = 0
    response_tokens: int | None = None
    completion_status: str = "unknown"  # complete, error, truncated

    # Interaction
    clarification_turns: int = 0
    retry_count: int = 0
    failure_reason: str | None = None

    # Cost (raw token counts from API, never estimated)
    cost_prompt_tokens: int | None = None
    cost_completion_tokens: int | None = None
    estimated_cost_usd: float | None = None

    # Raw response text (for verification, not analysis)
    response_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "model": self.model,
            "model_version": self.model_version,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "queue_time_seconds": self.queue_time_seconds,
            "request_latency_seconds": self.request_latency_seconds,
            "total_execution_time_seconds": self.total_execution_time_seconds,
            "prompt_characters": self.prompt_characters,
            "prompt_tokens_estimated": self.prompt_tokens_estimated,
            "prompt_tokens_exact": self.prompt_tokens_exact,
            "response_characters": self.response_characters,
            "response_tokens": self.response_tokens,
            "completion_status": self.completion_status,
            "clarification_turns": self.clarification_turns,
            "retry_count": self.retry_count,
            "failure_reason": self.failure_reason,
            "cost_prompt_tokens": self.cost_prompt_tokens,
            "cost_completion_tokens": self.cost_completion_tokens,
            "estimated_cost_usd": self.estimated_cost_usd,
        }

    def to_aimetrics_dict(self) -> dict[str, Any]:
        """Convert to kwargs compatible with AIMetrics population."""
        return {
            "prompt_tokens": self.prompt_tokens_exact or self.prompt_tokens_estimated,
            "context_tokens": self.prompt_tokens_exact or self.prompt_tokens_estimated,
            "total_tokens_supplied": (
                (self.prompt_tokens_exact or self.prompt_tokens_estimated)
                + (self.response_tokens or 0)
            ),
            "completion_tokens": self.response_tokens or 0,
            "clarification_questions": self.clarification_turns,
            "comprehension_accuracy": None,
            "first_attempt_correct": None,
            "iterations_to_correct": None,
        }


# ── Provider Interface ────────────────────────────────────────────────


class AIProvider(ABC):
    """Abstract interface for AI model providers.

    Every provider must expose consistent operations. Provider implementations
    may use different APIs internally, but externally they must behave identically.
    The benchmark framework should never know which provider is executing.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name (e.g. 'openai', 'anthropic')."""

    @property
    @abstractmethod
    def model(self) -> str:
        """Model identifier (e.g. 'gpt-4o', 'claude-3-opus-20240229')."""

    @property
    def model_version(self) -> str:
        """Model version string, if available."""
        return ""

    @abstractmethod
    def complete(self, prompt: str) -> ProviderResult:
        """Submit a prompt and return measurements.

        This is the core operation. Every provider implements this.
        The result must capture all observable measurements without
        interpreting them.
        """

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using this provider's tokenizer.

        Returns the exact token count if the provider supports it,
        otherwise an estimate.
        """

    def to_dict(self) -> dict[str, str]:
        """Provider metadata for reports."""
        return {
            "provider_name": self.provider_name,
            "model": self.model,
            "model_version": self.model_version,
        }


# ── Utility ───────────────────────────────────────────────────────────


def estimate_tokens_heuristic(text: str) -> int:
    """Approximate token count (4 chars ~ 1 token for code).

    Used when no model-specific tokenizer is available.
    """
    return max(1, len(text) // 4)


# ── Token Pricing (approximate, for cost estimation) ──────────────────


def _estimate_openai_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate USD cost for an OpenAI API call.

    Uses published pricing as of 2026-07. This is approximate —
    actual cost depends on caching, tier, and batch discounts.
    """
    pricing = {
        "gpt-4o": (2.50, 10.00),
        "gpt-4o-mini": (0.15, 0.60),
        "gpt-4-turbo": (10.00, 30.00),
        "gpt-4": (30.00, 60.00),
        "gpt-3.5-turbo": (0.50, 1.50),
    }
    model_lower = model.lower()
    rate = pricing.get(model_lower)
    if rate is None:
        for key, val in pricing.items():
            if key in model_lower:
                rate = val
                break
    if rate is None:
        return 0.0
    prompt_rate, completion_rate = rate
    return (prompt_tokens / 1_000_000 * prompt_rate) + (
        completion_tokens / 1_000_000 * completion_rate
    )


def _estimate_anthropic_cost(
    model: str, prompt_tokens: int, completion_tokens: int
) -> float:
    """Estimate USD cost for an Anthropic API call."""
    pricing = {
        "claude-3-opus": (15.00, 75.00),
        "claude-3-sonnet": (3.00, 15.00),
        "claude-3-haiku": (0.25, 1.25),
        "claude-3-5-sonnet": (3.00, 15.00),
    }
    model_lower = model.lower()
    rate = pricing.get(model_lower)
    if rate is None:
        for key, val in pricing.items():
            if key in model_lower:
                rate = val
                break
    if rate is None:
        return 0.0
    prompt_rate, completion_rate = rate
    return (prompt_tokens / 1_000_000 * prompt_rate) + (
        completion_tokens / 1_000_000 * completion_rate
    )


def _estimate_google_cost(
    model: str, prompt_tokens: int, completion_tokens: int
) -> float:
    """Estimate USD cost for a Google AI API call."""
    pricing = {
        "gemini-1.5-pro": (3.50, 10.50),
        "gemini-1.5-flash": (0.075, 0.30),
        "gemini-2.0-pro": (5.00, 15.00),
        "gemini-2.0-flash": (0.10, 0.40),
    }
    model_lower = model.lower()
    rate = pricing.get(model_lower)
    if rate is None:
        for key, val in pricing.items():
            if key in model_lower:
                rate = val
                break
    if rate is None:
        return 0.0
    prompt_rate, completion_rate = rate
    return (prompt_tokens / 1_000_000 * prompt_rate) + (
        completion_tokens / 1_000_000 * completion_rate
    )

"""AI provider abstraction layer.

Provider-independent interface for submitting prompts to AI models
and collecting measurements. The benchmark framework never knows which
provider is executing the benchmark.
"""

from __future__ import annotations

from benchmarks.providers.base import AIProvider, ProviderResult
from benchmarks.providers.openai_provider import OpenAIProvider
from benchmarks.providers.anthropic_provider import AnthropicProvider
from benchmarks.providers.google_provider import GoogleProvider
from benchmarks.providers.local_provider import LocalProvider


PROVIDER_REGISTRY: dict[str, type[AIProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "google": GoogleProvider,
    "local": LocalProvider,
}


def create_provider(
    name: str,
    model: str = "",
    api_key: str | None = None,
    **kwargs,
) -> AIProvider:
    """Factory: create a provider by name.

    Args:
        name: Provider name ('openai', 'anthropic', 'google', 'local').
        model: Model identifier. Uses provider default if empty.
        api_key: Optional API key. Falls back to environment variable.
        **kwargs: Provider-specific configuration.

    Returns:
        An initialized AIProvider instance.

    Raises:
        ValueError: If provider name is unknown.
    """
    cls = PROVIDER_REGISTRY.get(name)
    if cls is None:
        known = ", ".join(sorted(PROVIDER_REGISTRY))
        raise ValueError(
            f"Unknown provider: '{name}'. Known providers: {known}"
        )
    return cls(model=model, api_key=api_key, **kwargs)


def list_providers() -> list[str]:
    """Return sorted list of registered provider names."""
    return sorted(PROVIDER_REGISTRY)


__all__ = [
    "AIProvider",
    "ProviderResult",
    "OpenAIProvider",
    "AnthropicProvider",
    "GoogleProvider",
    "LocalProvider",
    "create_provider",
    "list_providers",
]

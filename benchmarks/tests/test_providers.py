"""Tests for AI provider abstraction layer.

Covers acceptance (interface contract, serialization, factory) and
regression (stable schema, historical compatibility).
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from benchmarks.providers.base import (
    ProviderResult,
    AIProvider,
    estimate_tokens_heuristic,
    _estimate_openai_cost,
    _estimate_anthropic_cost,
    _estimate_google_cost,
)


# ── ProviderResult Tests ──────────────────────────────────────────────


class TestProviderResult:
    """Verify ProviderResult dataclass."""

    def test_defaults(self):
        result = ProviderResult()
        assert result.provider_name == ""
        assert result.completion_status == "unknown"
        assert result.failure_reason is None

    def test_to_dict_includes_all_keys(self):
        result = ProviderResult(
            provider_name="test",
            model="test-model",
            request_latency_seconds=1.5,
            prompt_characters=100,
            response_tokens=50,
        )
        d = result.to_dict()
        assert d["provider_name"] == "test"
        assert d["model"] == "test-model"
        assert d["request_latency_seconds"] == 1.5
        assert d["prompt_characters"] == 100
        assert d["response_tokens"] == 50
        assert d["completion_status"] == "unknown"
        assert d["failure_reason"] is None

    def test_to_dict_allows_none(self):
        result = ProviderResult(
            provider_name="test",
            model="test",
            prompt_tokens_exact=None,
            cost_prompt_tokens=None,
        )
        d = result.to_dict()
        assert d["prompt_tokens_exact"] is None
        assert d["cost_prompt_tokens"] is None

    def test_to_aimetrics_dict(self):
        result = ProviderResult(
            provider_name="openai",
            model="gpt-4o",
            prompt_tokens_exact=150,
            prompt_tokens_estimated=160,
            response_tokens=50,
        )
        d = result.to_aimetrics_dict()
        assert d["prompt_tokens"] == 150
        assert d["completion_tokens"] == 50
        assert d["total_tokens_supplied"] == 200
        assert d["comprehension_accuracy"] is None

    def test_to_aimetrics_dict_fallback_estimate(self):
        result = ProviderResult(
            provider_name="local",
            model="llama3",
            prompt_tokens_exact=None,
            prompt_tokens_estimated=100,
        )
        d = result.to_aimetrics_dict()
        assert d["prompt_tokens"] == 100

    def test_serialization_roundtrip(self):
        result = ProviderResult(
            provider_name="openai",
            model="gpt-4o",
            model_version="2024-08-06",
            request_id="req_123",
            timestamp="2026-07-07T12:00:00",
            queue_time_seconds=0.1,
            request_latency_seconds=2.5,
            total_execution_time_seconds=2.6,
            prompt_characters=500,
            prompt_tokens_estimated=125,
            prompt_tokens_exact=120,
            response_characters=200,
            response_tokens=50,
            completion_status="complete",
            retry_count=0,
            cost_prompt_tokens=120,
            cost_completion_tokens=50,
            estimated_cost_usd=0.001,
            response_text="Hello!",
        )
        d = result.to_dict()
        restored = ProviderResult(**d)
        assert restored.provider_name == result.provider_name
        assert restored.model == result.model
        assert restored.request_latency_seconds == result.request_latency_seconds
        assert restored.prompt_tokens_exact == result.prompt_tokens_exact
        assert restored.estimated_cost_usd == result.estimated_cost_usd


# ── Provider Interface Tests ──────────────────────────────────────────


class TestAIProviderInterface:
    """Verify the abstract interface contract is enforceable."""

    def test_cannot_instantiate_abstract(self):
        """AIProvider ABC cannot be instantiated directly."""
        try:
            AIProvider()  # type: ignore
            assert False, "Should have raised TypeError"
        except TypeError:
            pass

    def test_concrete_provider_must_implement_interface(self):
        """A minimal provider must implement all abstract methods."""
        class MinimalProvider(AIProvider):
            @property
            def provider_name(self) -> str:
                return "minimal"

            @property
            def model(self) -> str:
                return "minimal-model"

            def complete(self, prompt: str) -> ProviderResult:
                return ProviderResult(
                    provider_name=self.provider_name,
                    model=self.model,
                )

            def count_tokens(self, text: str) -> int:
                return estimate_tokens_heuristic(text)

        p = MinimalProvider()
        assert p.provider_name == "minimal"
        assert p.model == "minimal-model"
        assert p.model_version == ""
        result = p.complete("hello")
        assert isinstance(result, ProviderResult)
        assert result.provider_name == "minimal"
        assert p.count_tokens("hello world") >= 1
        assert p.to_dict() == {
            "provider_name": "minimal",
            "model": "minimal-model",
            "model_version": "",
        }


# ── Provider Factory Tests ────────────────────────────────────────────


class TestProviderFactory:
    """Verify provider factory."""

    def test_create_openai(self):
        from benchmarks.providers import create_provider
        provider = create_provider("openai", model="gpt-4o-mini")
        assert provider.provider_name == "openai"
        assert provider.model == "gpt-4o-mini"

    def test_create_anthropic(self):
        from benchmarks.providers import create_provider
        provider = create_provider("anthropic", model="claude-3-haiku-20240307")
        assert provider.provider_name == "anthropic"
        assert provider.model == "claude-3-haiku-20240307"

    def test_create_google(self):
        from benchmarks.providers import create_provider
        provider = create_provider("google", model="gemini-1.5-flash")
        assert provider.provider_name == "google"
        assert provider.model == "gemini-1.5-flash"

    def test_create_local(self):
        from benchmarks.providers import create_provider
        provider = create_provider("local", model="llama3.2")
        assert provider.provider_name == "local"
        assert provider.model == "llama3.2"

    def test_create_unknown_provider_raises(self):
        from benchmarks.providers import create_provider
        try:
            create_provider("nonexistent")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Unknown provider" in str(e)

    def test_list_providers(self):
        from benchmarks.providers import list_providers
        names = list_providers()
        assert "openai" in names
        assert "anthropic" in names
        assert "google" in names
        assert "local" in names


# ── Provider Implementation Tests (mocked) ────────────────────────────


class TestOpenAIProviderMocked:
    """Verify OpenAI provider interface using mocks."""

    def test_complete_returns_provider_result(self):
        from benchmarks.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="test-key")

        mock_response = MagicMock()
        mock_response.id = "chatcmpl_test"
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello!"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        provider._client = mock_client

        result = provider.complete("Say hello")
        assert isinstance(result, ProviderResult)
        assert result.provider_name == "openai"
        assert result.model == "gpt-4o"
        assert result.completion_status == "complete"
        assert result.prompt_tokens_exact == 10
        assert result.response_tokens == 5
        assert result.response_text == "Hello!"
        assert result.request_latency_seconds > 0

    def test_complete_handles_error(self):
        from benchmarks.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="test-key")

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RuntimeError("API error")
        provider._client = mock_client

        result = provider.complete("Say hello")
        assert result.completion_status == "error"
        assert result.failure_reason is not None

    def test_count_tokens_heuristic_fallback(self):
        from benchmarks.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="test-key")
        count = provider.count_tokens("hello world")
        assert count >= 1


class TestAnthropicProviderMocked:
    """Verify Anthropic provider interface using mocks."""

    def test_complete_returns_provider_result(self):
        from benchmarks.providers.anthropic_provider import AnthropicProvider

        provider = AnthropicProvider(api_key="test-key")

        mock_response = MagicMock()
        mock_response.id = "msg_test"
        mock_response.stop_reason = "end_turn"
        block = MagicMock()
        block.text = "Hello from Claude"
        mock_response.content = [block]
        mock_response.usage.input_tokens = 15
        mock_response.usage.output_tokens = 8

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_client.messages.count_tokens.return_value = MagicMock(input_tokens=15)
        provider._client = mock_client

        result = provider.complete("Say hello")
        assert isinstance(result, ProviderResult)
        assert result.provider_name == "anthropic"
        assert result.completion_status == "complete"
        assert result.prompt_tokens_exact == 15
        assert result.response_tokens == 8

    def test_complete_handles_error(self):
        from benchmarks.providers.anthropic_provider import AnthropicProvider

        provider = AnthropicProvider(api_key="test-key")
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = RuntimeError("API error")
        provider._client = mock_client

        result = provider.complete("Say hello")
        assert result.completion_status == "error"
        assert result.failure_reason is not None


class TestGoogleProviderMocked:
    """Verify Google provider interface using mocks."""

    def test_complete_returns_provider_result(self):
        from benchmarks.providers.google_provider import GoogleProvider

        provider = GoogleProvider(api_key="test-key")

        mock_response = MagicMock()
        mock_response.text = "Hello from Gemini"
        mock_candidate = MagicMock()
        mock_candidate.finish_reason.name = "STOP"
        mock_response.candidates = [mock_candidate]
        mock_response.usage_metadata.prompt_token_count = 12
        mock_response.usage_metadata.candidates_token_count = 6

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model.count_tokens.return_value = MagicMock(total_tokens=12)
        provider._client = mock_model

        result = provider.complete("Say hello")
        assert isinstance(result, ProviderResult)
        assert result.provider_name == "google"
        assert result.completion_status == "complete"
        assert result.prompt_tokens_exact == 12
        assert result.response_tokens == 6

    def test_complete_handles_error(self):
        from benchmarks.providers.google_provider import GoogleProvider

        provider = GoogleProvider(api_key="test-key")
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = RuntimeError("API error")
        provider._client = mock_model

        result = provider.complete("Say hello")
        assert result.completion_status == "error"
        assert result.failure_reason is not None


class TestLocalProviderMocked:
    """Verify Local provider interface using mocks."""

    def test_complete_returns_provider_result(self):
        from benchmarks.providers.local_provider import LocalProvider

        provider = LocalProvider(model="llama3.2", base_url="http://localhost:9999/v1")

        mock_response = MagicMock()
        mock_response.id = "local_test"
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello from local"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        provider._client = mock_client

        result = provider.complete("Say hello")
        assert isinstance(result, ProviderResult)
        assert result.provider_name == "local"
        assert result.model == "llama3.2"
        assert result.completion_status == "complete"
        assert result.response_text == "Hello from local"

    def test_complete_handles_error(self):
        from benchmarks.providers.local_provider import LocalProvider

        provider = LocalProvider(model="llama3.2", base_url="http://localhost:9999/v1")
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RuntimeError("Connection refused")
        provider._client = mock_client

        result = provider.complete("Say hello")
        assert result.completion_status == "error"
        assert result.failure_reason is not None


# ── Token Estimation Tests ────────────────────────────────────────────


class TestTokenEstimation:
    """Verify token estimation utilities."""

    def test_heuristic(self):
        assert estimate_tokens_heuristic("") == 1
        assert estimate_tokens_heuristic("a") == 1
        assert estimate_tokens_heuristic("abcd") == 1
        assert estimate_tokens_heuristic("abcdefgh") == 2

    def test_openai_cost_estimation(self):
        cost = _estimate_openai_cost("gpt-4o", 1000, 500)
        assert cost > 0
        assert cost < 1.0  # sanity: $1K tokens shouldn't cost $1

        cost_unknown = _estimate_openai_cost("unknown-model", 1000, 500)
        assert cost_unknown == 0.0

    def test_anthropic_cost_estimation(self):
        cost = _estimate_anthropic_cost("claude-3-5-sonnet", 1000, 500)
        assert cost > 0
        assert cost < 1.0

    def test_google_cost_estimation(self):
        cost = _estimate_google_cost("gemini-2.0-flash", 1000, 500)
        assert cost > 0
        assert cost < 1.0


# ── B1 Provider Integration Tests ─────────────────────────────────────


class TestB1WithProvider:
    """Verify B1 benchmark integrates correctly with AI providers."""

    def test_b1_with_provider(self, tmp_path: Path):
        from benchmarks.b1_understanding.run import run
        from benchmarks.framework.metrics import RepositoryMetrics

        (tmp_path / "main.ail").write_text("fn main() { return 42; }\n")

        from benchmarks.providers.base import ProviderResult

        class FakeProvider(AIProvider):
            @property
            def provider_name(self) -> str:
                return "test_provider"

            @property
            def model(self) -> str:
                return "test-model"

            def complete(self, prompt: str) -> ProviderResult:
                return ProviderResult(
                    provider_name=self.provider_name,
                    model=self.model,
                    prompt_tokens_exact=50,
                    prompt_tokens_estimated=50,
                    response_tokens=10,
                    completion_status="complete",
                    response_text="This codebase returns 42.",
                )

            def count_tokens(self, text: str) -> int:
                return len(text) // 3

        repo = RepositoryMetrics(files=1, loc=1, function_count=1)
        result = run(dataset_path=tmp_path, repo_metrics=repo, provider=FakeProvider())

        assert result.ai is not None
        assert result.ai.prompt_tokens == 50
        assert result.ai.completion_tokens == 10
        assert result.ai.total_tokens_supplied == 60
        assert "test_provider" in result.ai.token_source_type

    def test_b1_without_provider_fallback(self, tmp_path: Path):
        from benchmarks.b1_understanding.run import run
        from benchmarks.framework.metrics import RepositoryMetrics

        (tmp_path / "main.ail").write_text("fn main() { return 42; }\n")

        repo = RepositoryMetrics(files=1, loc=1)
        result = run(dataset_path=tmp_path, repo_metrics=repo)

        assert result.ai is not None
        assert result.ai.context_tokens > 0
        assert result.ai.token_source_type == "ailang_approximate"


# ── Schema Stability Tests (Regression) ───────────────────────────────


class TestProviderSchemaStability:
    """Verify provider data schemas remain stable across versions.

    These tests ensure that the JSON schema of ProviderResult and
    CalibrationReport does not change unexpectedly.
    """

    def test_provider_result_schema_has_required_fields(self):
        """All required fields must be present in to_dict()."""
        result = ProviderResult(
            provider_name="openai",
            model="gpt-4o",
        )
        d = result.to_dict()

        required_fields = [
            "provider_name", "model", "model_version",
            "request_id", "timestamp",
            "queue_time_seconds", "request_latency_seconds",
            "total_execution_time_seconds",
            "prompt_characters", "prompt_tokens_estimated", "prompt_tokens_exact",
            "response_characters", "response_tokens", "completion_status",
            "clarification_turns", "retry_count", "failure_reason",
            "cost_prompt_tokens", "cost_completion_tokens", "estimated_cost_usd",
        ]
        for field in required_fields:
            assert field in d, f"Missing required field: {field}"

    def test_provider_result_serializable(self):
        """ProviderResult.to_dict() must be JSON-serializable."""
        result = ProviderResult(
            provider_name="openai",
            model="gpt-4o",
            request_latency_seconds=0.5,
        )
        d = result.to_dict()
        json_str = json.dumps(d)
        restored = json.loads(json_str)
        assert restored["provider_name"] == "openai"
        assert restored["request_latency_seconds"] == 0.5

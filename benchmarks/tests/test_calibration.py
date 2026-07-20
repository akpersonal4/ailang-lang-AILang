"""Tests for AI provider calibration.

Verifies that the calibration module correctly exercises providers
and validates measurement infrastructure. Does NOT compare providers.
"""

from __future__ import annotations

import json
from pathlib import Path

from benchmarks.providers.base import AIProvider, ProviderResult


class TestCalibrationExecution:
    """Verify calibration execution logic."""

    def test_calibration_runs_against_providers(self, tmp_path: Path):
        from benchmarks.calibration.run import CALIBRATION_PROMPTS, run_calibration

        class FakeProvider(AIProvider):
            @property
            def provider_name(self) -> str:
                return "fake"

            @property
            def model(self) -> str:
                return "fake-model"

            def complete(self, prompt: str) -> ProviderResult:
                return ProviderResult(
                    provider_name=self.provider_name,
                    model=self.model,
                    prompt_characters=len(prompt),
                    prompt_tokens_estimated=len(prompt) // 4,
                    response_text="calibration ok",
                    response_characters=15,
                    response_tokens=5,
                    completion_status="complete",
                    request_latency_seconds=0.01,
                )

            def count_tokens(self, text: str) -> int:
                return len(text) // 4

        providers = [FakeProvider()]
        report = run_calibration(
            providers=providers, output_dir=str(tmp_path), quiet=True
        )

        assert len(report.runs) == len(CALIBRATION_PROMPTS)
        assert len(report.errors) == 0

        for run_entry in report.runs:
            assert run_entry.prompt_name in [p["name"] for p in CALIBRATION_PROMPTS]
            assert run_entry.provider_name == "fake"
            assert run_entry.result.completion_status == "complete"

    def test_calibration_reports_errors(self, tmp_path: Path):
        from benchmarks.calibration.run import run_calibration

        class BrokenProvider(AIProvider):
            @property
            def provider_name(self) -> str:
                return "broken"

            @property
            def model(self) -> str:
                return "broken-model"

            def complete(self, prompt: str) -> ProviderResult:
                raise RuntimeError("Provider unavailable")

            def count_tokens(self, text: str) -> int:
                return 0

        providers = [BrokenProvider()]
        report = run_calibration(providers=providers, quiet=True)

        assert len(report.errors) > 0
        assert any("Provider unavailable" in e for e in report.errors)

    def test_calibration_with_no_providers(self):
        from benchmarks.calibration.run import run_calibration

        report = run_calibration(providers=[], quiet=True)
        assert len(report.errors) == 1
        assert "No providers" in report.errors[0]

    def test_calibration_report_serializable(self, tmp_path: Path):
        from benchmarks.calibration.run import CALIBRATION_PROMPTS, run_calibration

        class FakeProvider(AIProvider):
            @property
            def provider_name(self) -> str:
                return "fake"

            @property
            def model(self) -> str:
                return "fake-model"

            def complete(self, prompt: str) -> ProviderResult:
                return ProviderResult(
                    provider_name=self.provider_name,
                    model=self.model,
                    completion_status="complete",
                )

            def count_tokens(self, text: str) -> int:
                return 0

        providers = [FakeProvider()]
        report = run_calibration(
            providers=providers, output_dir=str(tmp_path), quiet=True
        )

        json_str = json.dumps(report.to_dict(), indent=2, default=str)
        restored = json.loads(json_str)
        assert restored["calibration_version"] == "0.1.0"
        assert len(restored["runs"]) == len(CALIBRATION_PROMPTS)
        assert "environment" in restored
        assert "errors" in restored


class TestCalibrationPrompts:
    """Verify calibration prompts are valid."""

    def test_prompts_have_required_fields(self):
        from benchmarks.calibration.run import CALIBRATION_PROMPTS

        for p in CALIBRATION_PROMPTS:
            assert "name" in p
            assert "prompt" in p
            assert len(p["name"]) > 0
            assert len(p["prompt"]) > 0

    def test_prompts_diverse(self):
        from benchmarks.calibration.run import CALIBRATION_PROMPTS

        names = [p["name"] for p in CALIBRATION_PROMPTS]
        assert names == ["short_response", "code_understanding", "token_counting"]

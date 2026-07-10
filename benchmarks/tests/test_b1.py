"""Tests for B1 — AI Repository Understanding Benchmark."""

from __future__ import annotations

from pathlib import Path
from benchmarks.framework.metrics import (
    RepositoryMetrics,
    AIMetrics,
    EngineeringMetrics,
    BenchmarkResult,
)


class TestB1Run:
    """Verify B1 benchmark execution."""

    def test_run_produces_result(self, tmp_path: Path):
        from benchmarks.b1_understanding.run import run

        (tmp_path / "main.ail").write_text(
            "fn main() { return 42; }\n"
        )

        repo = RepositoryMetrics(files=1, loc=1, function_count=1)
        result = run(dataset_path=tmp_path, repo_metrics=repo)
        assert isinstance(result, BenchmarkResult)
        assert result.benchmark_name == "B1 — AI Repository Understanding"
        assert result.repository.files == 1
        assert result.ai is not None

    def test_estimates_tokens(self, tmp_path: Path):
        from benchmarks.b1_understanding.run import run

        (tmp_path / "main.ail").write_text(
            "fn hello() { return \"hello world\"; }\n"
        )

        repo = RepositoryMetrics(files=1, loc=1)
        result = run(dataset_path=tmp_path, repo_metrics=repo)
        assert result.ai.context_tokens > 0

    def test_accepts_ai_results_from_kwargs(self, tmp_path: Path):
        from benchmarks.b1_understanding.run import run

        (tmp_path / "main.ail").write_text("fn main() { return 0; }")
        repo = RepositoryMetrics(files=1, loc=1)

        ai_input = {
            "prompt_tokens": 500,
            "context_tokens": 1200,
            "total_tokens_supplied": 1700,
            "completion_tokens": 200,
            "clarification_questions": 1,
            "comprehension_accuracy": 0.92,
            "first_attempt_correct": True,
            "iterations_to_correct": 1,
        }

        result = run(dataset_path=tmp_path, repo_metrics=repo, ai_results=ai_input)
        assert result.ai.prompt_tokens == 500
        assert result.ai.comprehension_accuracy == 0.92
        assert result.ai.first_attempt_correct is True


class TestEstimateTokens:
    """Verify approximate token counting."""

    def test_estimate_tokens(self):
        from benchmarks.b1_understanding.run import estimate_tokens
        assert estimate_tokens("hello world") == 2  # 11 chars // 4
        assert estimate_tokens("") == 1  # minimum
        assert estimate_tokens("a") == 1  # minimum

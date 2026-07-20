"""Tests for the benchmark runner."""

from __future__ import annotations

from pathlib import Path

from benchmarks.framework.metrics import BenchmarkResult
from benchmarks.framework.runner import (
    RunConfiguration,
    compute_repo_metrics_from_dataset,
)


def fixture_result(
    dataset_path: Path,
    repo_metrics,
    output_dir=None,
    quiet=False,
    **kwargs,
) -> BenchmarkResult:
    """A test benchmark function that returns a minimal result."""
    from benchmarks.framework.environment import snapshot
    from benchmarks.framework.metrics import (
        AIMetrics,
        BenchmarkResult,
        EngineeringMetrics,
    )
    from benchmarks.framework.reporting import generate_run_id

    env = snapshot()
    return BenchmarkResult(
        benchmark_name="test",
        benchmark_version="0.1.0",
        run_id=generate_run_id(),
        timestamp=env["timestamp"],
        repository=repo_metrics,
        ai=AIMetrics(prompt_tokens=100),
        engineering=EngineeringMetrics(framework_version="0.1.0"),
        environment_snapshot=env,
    )


class TestRunConfiguration:
    """Verify RunConfiguration dataclass."""

    def test_defaults(self):
        config = RunConfiguration(
            benchmark_name="test",
            benchmark_version="0.1.0",
            dataset_path=Path("/tmp"),
        )
        assert config.benchmark_name == "test"
        assert config.quiet is False
        assert config.extra is None

    def test_custom_values(self):
        config = RunConfiguration(
            benchmark_name="b1",
            benchmark_version="0.1.0",
            dataset_path=Path("/tmp"),
            quiet=True,
            extra={"model": "claude"},
        )
        assert config.quiet is True
        assert config.extra["model"] == "claude"


class TestComputeRepoMetricsFromDataset:
    """Verify repo metrics extraction from a dataset directory."""

    def test_returns_metrics(self, tmp_path: Path):
        (tmp_path / "main.ail").write_text("fn main() { return 0; }")
        metrics = compute_repo_metrics_from_dataset(tmp_path)
        assert metrics.files == 1
        assert metrics.loc == 1
        assert metrics.function_count == 1

    def test_empty_directory(self, tmp_path: Path):
        metrics = compute_repo_metrics_from_dataset(tmp_path)
        assert metrics.files == 0
        assert metrics.loc == 0


class TestRunnerIntegration:
    """Verify runner integrates with framework components."""

    def test_runner_calls_benchmark_fn(self, tmp_path: Path):
        (tmp_path / "main.ail").write_text("fn main() { return 0; }")

        config = RunConfiguration(
            benchmark_name="integration_test",
            benchmark_version="0.1.0",
            dataset_path=tmp_path,
            output_dir=tmp_path / "results",
            quiet=True,
        )

        from benchmarks.framework.runner import run_benchmark

        result = run_benchmark(config, fixture_result)

        assert result.benchmark_name == "integration_test"
        assert result.repository.files >= 1
        assert result.engineering.execution_time_seconds > 0
        assert result.environment_snapshot["git"]["commit"] != "unknown"

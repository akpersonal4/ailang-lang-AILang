"""Tests for measurement collection."""

from __future__ import annotations

import pytest
from pathlib import Path
from benchmarks.framework.metrics import (
    compute_repo_metrics,
    compute_repeatability_hash,
    RepositoryMetrics,
    AIMetrics,
    EngineeringMetrics,
    BenchmarkResult,
)


# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def framework_dir() -> Path:
    """Return a directory with known test data."""
    here = Path(__file__).resolve().parent
    return here.parent / "framework"


# ── Acceptance Tests ─────────────────────────────────────────────────


class TestComputeRepoMetrics:
    """Verify repository metrics are computed correctly."""

    def test_returns_metrics_object(self, tmp_path: Path):
        metrics = compute_repo_metrics(tmp_path)
        assert isinstance(metrics, RepositoryMetrics)

    def test_empty_directory(self, tmp_path: Path):
        metrics = compute_repo_metrics(tmp_path)
        assert metrics.files == 0
        assert metrics.loc == 0
        assert metrics.function_count == 0
        assert metrics.variable_count == 0
        assert metrics.import_count == 0

    def test_counts_functions(self, tmp_path: Path):
        (tmp_path / "test.ail").write_text(
            "fn main() { return 1; }\n"
            "fn add(a, b) { return a + b; }\n"
            "fn helper() { return 0; }\n"
        )
        metrics = compute_repo_metrics(tmp_path)
        assert metrics.function_count == 3
        assert metrics.symbol_count == 3

    def test_counts_variables(self, tmp_path: Path):
        (tmp_path / "test.ail").write_text(
            "let x = 10;\n"
            "let name = \"hello\";\n"
            "fn main() {\n"
            "  let result = x;\n"
            "  return result;\n"
            "}\n"
        )
        metrics = compute_repo_metrics(tmp_path)
        assert metrics.variable_count >= 1
        assert metrics.function_count == 1

    def test_counts_imports(self, tmp_path: Path):
        (tmp_path / "test.ail").write_text(
            "import math;\n"
            "import string;\n"
            "import list;\n"
            "fn main() { return 0; }\n"
        )
        metrics = compute_repo_metrics(tmp_path)
        assert metrics.import_count == 3
        assert metrics.dependency_count == 3

    def test_counts_loc(self, tmp_path: Path):
        (tmp_path / "test.ail").write_text(
            "fn main() {\n"
            "  return 1 + 2;\n"
            "}\n"
        )
        metrics = compute_repo_metrics(tmp_path)
        assert metrics.loc == 3  # 3 non-empty lines


class TestComputeRepeatabilityHash:
    """Verify repeatability hashing is deterministic."""

    def test_deterministic(self):
        data = {"a": 1, "b": 2, "c": [3, 4, 5]}
        h1 = compute_repeatability_hash(data)
        h2 = compute_repeatability_hash(data)
        assert h1 == h2

    def test_different_data_produces_different_hash(self):
        d1 = {"a": 1, "b": 2}
        d2 = {"a": 1, "b": 3}
        assert compute_repeatability_hash(d1) != compute_repeatability_hash(d2)

    def test_key_order_independent(self):
        d1 = {"z": 1, "a": 2}
        d2 = {"a": 2, "z": 1}
        assert compute_repeatability_hash(d1) == compute_repeatability_hash(d2)


class TestAIMetrics:
    """Verify AI metrics dataclass works correctly."""

    def test_defaults(self):
        ai = AIMetrics()
        assert ai.prompt_tokens == 0
        assert ai.comprehension_accuracy is None

    def test_can_set_values(self):
        ai = AIMetrics(
            prompt_tokens=100,
            context_tokens=200,
            comprehension_accuracy=0.85,
            first_attempt_correct=True,
        )
        assert ai.prompt_tokens == 100
        assert ai.comprehension_accuracy == 0.85
        assert ai.first_attempt_correct is True


class TestBenchmarkResult:
    """Verify BenchmarkResult construction and serialization."""

    def test_to_dict_contains_all_keys(self):
        repo = RepositoryMetrics(files=5, loc=100)
        ai = AIMetrics(prompt_tokens=50)
        eng = EngineeringMetrics(execution_time_seconds=1.5)

        result = BenchmarkResult(
            benchmark_name="test",
            benchmark_version="0.1.0",
            run_id="run_001",
            timestamp="2026-01-01T00:00:00",
            repository=repo,
            ai=ai,
            engineering=eng,
            environment_snapshot={"os": "test"},
        )

        d = result.to_dict()
        assert d["benchmark_name"] == "test"
        assert d["repository"]["files"] == 5
        assert d["ai"]["prompt_tokens"] == 50
        assert d["engineering"]["execution_time_seconds"] == 1.5
        assert d["environment_snapshot"]["os"] == "test"

    def test_ai_can_be_none(self):
        repo = RepositoryMetrics()
        eng = EngineeringMetrics()
        result = BenchmarkResult(
            benchmark_name="test",
            benchmark_version="0.1.0",
            run_id="run_001",
            timestamp="2026-01-01T00:00:00",
            repository=repo,
            ai=None,
            engineering=eng,
        )
        d = result.to_dict()
        assert d["ai"] is None

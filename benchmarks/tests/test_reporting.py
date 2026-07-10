"""Tests for report generation."""

from __future__ import annotations

import json
from pathlib import Path
from benchmarks.framework.metrics import (
    BenchmarkResult,
    RepositoryMetrics,
    AIMetrics,
    EngineeringMetrics,
)
from benchmarks.framework.reporting import (
    generate_run_id,
    write_json,
    write_markdown,
    write_summary,
)


def make_sample_result() -> BenchmarkResult:
    """Create a sample BenchmarkResult for testing."""
    repo = RepositoryMetrics(
        files=10, loc=500, module_count=3, symbol_count=25,
        function_count=20, variable_count=5, import_count=8,
        doc_size_bytes=2000,
    )
    ai = AIMetrics(
        prompt_tokens=100, context_tokens=400, total_tokens_supplied=500,
        completion_tokens=50, clarification_questions=2,
        comprehension_accuracy=0.85, first_attempt_correct=True,
        iterations_to_correct=1, token_source_type="ailang",
    )
    eng = EngineeringMetrics(
        execution_time_seconds=3.5, repeatability_hash="abc123",
        error_count=1, errors=["Sample error"],
        framework_version="0.1.0",
    )
    return BenchmarkResult(
        benchmark_name="test_benchmark",
        benchmark_version="0.1.0",
        run_id="run_test_001",
        timestamp="2026-01-01T00:00:00",
        repository=repo,
        ai=ai,
        engineering=eng,
        environment_snapshot={
            "os": {"system": "TestOS", "release": "1.0", "machine": "x86_64"},
            "python": {"version": "3.11"},
            "git": {"commit": "abc123def", "branch": "main", "dirty": False},
        },
    )


class TestGenerateRunId:
    """Verify run ID generation."""

    def test_generates_unique_ids(self):
        ids = {generate_run_id() for _ in range(1000)}
        assert len(ids) == 1000  # nanosecond precision guarantees uniqueness

    def test_ids_are_sortable(self):
        ids = sorted([generate_run_id() for _ in range(10)])
        assert ids == sorted(ids)  # chronological order


class TestWriteJSON:
    """Verify JSON report generation."""

    def test_writes_to_disk(self, tmp_path: Path):
        result = make_sample_result()
        path = write_json(result, output_dir=tmp_path)
        assert path.exists()
        assert path.suffix == ".json"

    def test_output_is_valid_json(self, tmp_path: Path):
        result = make_sample_result()
        path = write_json(result, output_dir=tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["benchmark_name"] == "test_benchmark"
        assert data["repository"]["files"] == 10

    def test_contains_environment(self, tmp_path: Path):
        result = make_sample_result()
        write_json(result, output_dir=tmp_path)
        run_dir = tmp_path / "test_benchmark" / "run_test_001"
        env_path = run_dir / "environment.json"
        assert env_path.exists()
        env = json.loads(env_path.read_text(encoding="utf-8"))
        assert env["os"]["system"] == "TestOS"


class TestWriteMarkdown:
    """Verify Markdown report generation."""

    def test_writes_to_disk(self, tmp_path: Path):
        result = make_sample_result()
        path = write_markdown(result, output_dir=tmp_path)
        assert path.exists()
        assert path.suffix == ".md"

    def test_contains_metrics(self, tmp_path: Path):
        result = make_sample_result()
        path = write_markdown(result, output_dir=tmp_path)
        content = path.read_text(encoding="utf-8")
        assert "test_benchmark" in content
        assert "Repository Metrics" in content
        assert "AI Metrics" in content
        assert "Engineering Metrics" in content
        assert "Environment" in content

    def test_does_not_overwrite(self, tmp_path: Path):
        """Each run produces a unique path (by run_id)."""
        from benchmarks.framework.reporting import generate_run_id

        r1 = make_sample_result()
        r1.run_id = generate_run_id()
        r2 = make_sample_result()
        r2.run_id = generate_run_id()
        p1 = write_json(r1, output_dir=tmp_path)
        p2 = write_json(r2, output_dir=tmp_path)
        assert p1 != p2  # different run_dir


class TestWriteSummary:
    """Verify summary generation."""

    def test_writes_summary_json(self, tmp_path: Path):
        results = [make_sample_result(), make_sample_result()]
        path = write_summary(results, output_dir=tmp_path)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["total_runs"] == 2
        assert len(data["runs"]) == 2

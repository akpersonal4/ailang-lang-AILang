"""Benchmark runner — orchestrates benchmark execution.

Keeps benchmark methodology separate from benchmark results. The runner
calls measurement functions but never interprets the results.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from benchmarks.framework.dataset import scan_project
from benchmarks.framework.environment import snapshot
from benchmarks.framework.metrics import (
    BenchmarkResult,
    RepositoryMetrics,
)
from benchmarks.framework.reporting import write_json, write_markdown

BenchmarkFunc = Callable[..., BenchmarkResult]


@dataclass
class RunConfiguration:
    """Configuration for a single benchmark run."""

    benchmark_name: str
    benchmark_version: str
    dataset_path: Path
    output_dir: Path | None = None
    quiet: bool = False
    extra: dict[str, Any] | None = None


def run_benchmark(
    config: RunConfiguration,
    benchmark_fn: BenchmarkFunc,
    **kwargs: Any,
) -> BenchmarkResult:
    """Execute a benchmark and produce results.

    This is the core execution path. It:
    1. Records the environment
    2. Scans the dataset for repository metrics
    3. Calls the benchmark-specific measurement function
    4. Collects engineering metrics
    5. Generates reports

    Returns the BenchmarkResult (also persisted to disk).
    """
    env = snapshot()
    start_time = time.perf_counter()

    if not config.dataset_path.is_dir():
        raise NotADirectoryError(
            f"Dataset not found: {config.dataset_path}. "
            "Did you initialize the datasets? Try: python -m benchmarks.setup"
        )

    repo_metrics = compute_repo_metrics_from_dataset(config.dataset_path)

    result = benchmark_fn(
        dataset_path=config.dataset_path,
        repo_metrics=repo_metrics,
        output_dir=config.output_dir,
        quiet=config.quiet,
        **(config.extra or {}),
        **kwargs,
    )

    result.benchmark_name = config.benchmark_name
    result.benchmark_version = config.benchmark_version

    elapsed = time.perf_counter() - start_time
    result.engineering.execution_time_seconds = elapsed
    result.environment_snapshot = env

    if config.output_dir:
        write_json(result, config.output_dir)
        write_markdown(result, config.output_dir)

    if not config.quiet:
        print(
            f"[BENCHMARK] {config.benchmark_name} — "
            f"{result.engineering.execution_time_seconds:.3f}s — "
            f"errors: {result.engineering.error_count}"
        )

    return result


def compute_repo_metrics_from_dataset(dataset_path: Path) -> RepositoryMetrics:
    """Compute repository metrics by scanning the dataset directory.

    Uses the dataset's scan_project function and converts to RepositoryMetrics.
    """
    metadata = scan_project(dataset_path, name=dataset_path.name)
    return RepositoryMetrics(
        files=metadata.file_count,
        loc=metadata.loc,
        module_count=metadata.module_count,
        symbol_count=metadata.symbol_count,
        function_count=metadata.function_count,
        variable_count=metadata.variable_count,
        import_count=metadata.dependency_count,
        doc_size_bytes=metadata.doc_size_bytes,
    )

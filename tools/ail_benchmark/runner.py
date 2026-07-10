# AILang Benchmark Runner: Runner
# Executes benchmarks via ail build / ail run with measurement pipeline

from __future__ import annotations

import statistics
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from ail_platform.project import get_project_root
from typing import Any


@dataclass
class MeasurementResult:
    """Result of a single measurement (build or run)."""

    time: float = 0.0
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""


@dataclass
class BenchmarkRun:
    """Result of a single benchmark iteration."""

    build: MeasurementResult = field(default_factory=MeasurementResult)
    run: MeasurementResult = field(default_factory=MeasurementResult)


@dataclass
class RunStats:
    """Aggregated statistics across multiple runs."""

    min: float = 0.0
    max: float = 0.0
    avg: float = 0.0
    median: float = 0.0


@dataclass
class RegressionInfo:
    """Regression detection result for a benchmark."""

    detected: bool = False
    build_regression_pct: float | None = None
    run_regression_pct: float | None = None


@dataclass
class BenchmarkResult:
    """Complete result for a single benchmark after all runs."""

    name: str
    path: str
    suite: str
    status: str  # "pass" | "fail" | "skip"
    error: str | None
    runs: list[BenchmarkRun] = field(default_factory=list)
    build_stats: RunStats = field(default_factory=RunStats)
    run_stats: RunStats = field(default_factory=RunStats)
    regression: RegressionInfo = field(default_factory=RegressionInfo)
    memory_kb: float | None = None
    baseline: dict[str, float] | None = None


def perform_measurement(
    cmd: list[str],
    cwd: Path,
    timeout: int,
) -> MeasurementResult:
    """Execute a command and measure wall-clock time.

    This is the core measurement primitive. Future metrics (CPU,
    allocation, profiling) can be added here without changing callers.
    """
    start = time.perf_counter()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
        )
        elapsed = time.perf_counter() - start
        return MeasurementResult(
            time=elapsed,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - start
        return MeasurementResult(
            time=elapsed,
            exit_code=-1,
            stdout="",
            stderr=f"TIMEOUT after {timeout}s",
        )
    except FileNotFoundError:
        return MeasurementResult(
            time=0.0,
            exit_code=-2,
            stdout="",
            stderr="Command not found. Is `ail` installed?",
        )


def compute_stats(values: list[float]) -> RunStats:
    """Compute min, max, avg, median from a list of times."""
    if not values:
        return RunStats()
    return RunStats(
        min=min(values),
        max=max(values),
        avg=statistics.mean(values),
        median=statistics.median(values),
    )


def run_benchmark(
    benchmark: "Benchmark",
    repeat: int = 3,
    timeout: int = 300,
    memory: bool = False,
    quiet: bool = False,
) -> BenchmarkResult:
    """Run a benchmark multiple times and compute aggregated results.

    Args:
        benchmark: The benchmark to run.
        repeat: Number of times to repeat (default 3).
        timeout: Per-command timeout in seconds.
        memory: Whether to measure peak memory.
        quiet: Suppress per-benchmark progress output.

    Returns:
        BenchmarkResult with aggregated statistics.
    """
    root = get_project_root()
    python = sys.executable

    result = BenchmarkResult(
        name=benchmark.name,
        path=str(benchmark.path),
        suite=benchmark.suite,
        status="pass",
        error=None,
    )

    # Extra CLI args for this benchmark (e.g., static_analyzer needs a file arg)
    extra_args = benchmark.args or []

    build_times: list[float] = []
    run_times: list[float] = []

    for i in range(repeat):
        if not quiet:
            print(f"  [{i + 1}/{repeat}] Building {benchmark.name}...")

        # Build step (no extra args needed for build)
        build_cmd = [python, "-m", "compiler", "build", str(benchmark.path)]
        build_measurement = perform_measurement(build_cmd, root, timeout)
        run = BenchmarkRun(build=build_measurement)

        if build_measurement.exit_code != 0:
            result.status = "fail"
            result.error = (
                f"Build failed (exit {build_measurement.exit_code}): "
                f"{build_measurement.stderr.strip()}"
            )
            if not quiet:
                print(f"  [FAIL] Build failed: {result.error[:120]}")
            result.runs.append(run)
            break

        if not quiet:
            print(f"  [{i + 1}/{repeat}] Running {benchmark.name}...")

        # Run step (append extra args if any)
        run_cmd = [python, "-m", "compiler", "run", str(benchmark.path)] + extra_args
        run_measurement = perform_measurement(run_cmd, root, timeout)
        run = BenchmarkRun(build=build_measurement, run=run_measurement)
        result.runs.append(run)

        if run_measurement.exit_code != 0:
            result.status = "fail"
            result.error = (
                f"Run failed (exit {run_measurement.exit_code}): "
                f"{run_measurement.stderr.strip()}"
            )
            if not quiet:
                print(f"  [FAIL] Run failed: {result.error[:120]}")
            break

        build_times.append(build_measurement.time)
        run_times.append(run_measurement.time)

        if not quiet:
            print(f"  [OK] {benchmark.name} — build {build_measurement.time:.3f}s, "
                  f"run {run_measurement.time:.3f}s")

    # Compute stats from successful runs only
    if build_times:
        result.build_stats = compute_stats(build_times)
    if run_times:
        result.run_stats = compute_stats(run_times)

    # Memory measurement (optional, last run only to minimize overhead)
    if memory and result.status == "pass":
        try:
            import tracemalloc

            tracemalloc.start()
            subprocess.run(
                [python, "-m", "compiler", "run", str(benchmark.path)] + extra_args,
                capture_output=True,
                text=True,
                cwd=root,
                timeout=timeout,
            )
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            result.memory_kb = peak / 1024
        except ImportError:
            result.memory_kb = None

    return result

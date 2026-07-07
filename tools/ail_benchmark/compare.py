# AILang Benchmark Runner: Comparison
# Baseline save/load/diff and regression detection

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def get_benchmark_dir(root: Path) -> Path:
    """Return the benchmarks data directory."""
    path = root / "generated" / "benchmarks"
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_baseline(results: list[dict], root: Path, name: str | None = None) -> Path:
    """Save benchmark results as a baseline JSON file.

    Args:
        results: List of benchmark result dicts.
        root: Project root path.
        name: Baseline name (default: 'baseline.json').

    Returns:
        Path to the saved baseline file.
    """
    bench_dir = get_benchmark_dir(root)
    filename = f"{name}.json" if name else "baseline.json"
    path = bench_dir / filename

    baseline = {
        "tool": "ail_benchmark",
        "type": "baseline",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmarks": {},
    }

    for r in results:
        baseline["benchmarks"][r["name"]] = {
            "build_time_avg": r.get("stats", {}).get("build_time", {}).get("avg", 0),
            "run_time_avg": r.get("stats", {}).get("run_time", {}).get("avg", 0),
            "build_time_min": r.get("stats", {}).get("build_time", {}).get("min", 0),
            "run_time_min": r.get("stats", {}).get("run_time", {}).get("min", 0),
        }

    path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    return path


def load_baseline(root: Path, name: str | None = None) -> dict[str, Any] | None:
    """Load a saved baseline.

    Args:
        root: Project root path.
        name: Baseline name (default: 'baseline.json').

    Returns:
        Baseline dict, or None if not found.
    """
    bench_dir = get_benchmark_dir(root)
    filename = f"{name}.json" if name else "baseline.json"
    path = bench_dir / filename

    if not path.is_file():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def detect_regressions(
    results: list[dict],
    baseline: dict[str, Any],
    threshold_pct: float = 20.0,
) -> list[dict]:
    """Compare results against a baseline and flag regressions.

    Modifies each result dict in-place, adding regression info.

    Args:
        results: List of benchmark result dicts (mutated in-place).
        baseline: Baseline data from load_baseline().
        threshold_pct: Percentage increase threshold (default 20%%).

    Returns:
        The same results list with regression info added.
    """
    bench_data = baseline.get("benchmarks", {})

    for r in results:
        name = r["name"]
        base = bench_data.get(name)
        if not base:
            r["baseline"] = None
            r["regression"] = {
                "detected": False,
                "build_regression_pct": None,
                "run_regression_pct": None,
            }
            continue

        build_base = base.get("build_time_avg", 0)
        run_base = base.get("run_time_avg", 0)
        build_current = r.get("stats", {}).get("build_time", {}).get("avg", 0)
        run_current = r.get("stats", {}).get("run_time", {}).get("avg", 0)

        build_pct = None
        run_pct = None

        if build_base > 0:
            build_pct = round((build_current - build_base) / build_base * 100, 1)
        if run_base > 0:
            run_pct = round((run_current - run_base) / run_base * 100, 1)

        detected = (build_pct is not None and build_pct > threshold_pct) or (
            run_pct is not None and run_pct > threshold_pct
        )

        r["baseline"] = {
            "build_time_avg": build_base,
            "run_time_avg": run_base,
        }
        r["regression"] = {
            "detected": detected,
            "build_regression_pct": build_pct,
            "run_regression_pct": run_pct,
        }

    return results

"""Report generation for benchmarks.

Produces two outputs per run:
1. Raw JSON — machine-readable, append-only history
2. Human-readable Markdown — formatted for review

Historical runs are never overwritten. Each run is stored by run_id.
"""

from __future__ import annotations

import itertools
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from benchmarks.framework.metrics import BenchmarkResult

# Monotonic counter ensures unique run IDs within a single process,
# regardless of system clock precision limitations.
_run_id_counter = itertools.count(1)


def generate_run_id() -> str:
    """Generate a unique, sortable run identifier.

    Uses a monotonic counter combined with a timestamp to guarantee
    uniqueness within a single process across all platforms.
    """
    seq = next(_run_id_counter)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"run_{ts}_{seq:06d}"


def _default_output_dir() -> Path:
    """Default output directory: benchmarks/results/"""
    here = Path(__file__).resolve().parent.parent
    return here / "results"


def write_json(result: BenchmarkResult, output_dir: Path | None = None) -> Path:
    """Write raw measurement data as JSON.

    Never overwrites. Each run_id produces a unique file.
    """
    out = output_dir or _default_output_dir()
    run_dir = out / result.benchmark_name / result.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "measurements.json"
    path.write_text(
        json.dumps(result.to_dict(), indent=2, default=str),
        encoding="utf-8",
    )
    _write_environment(result, run_dir)
    return path


def _write_environment(result: BenchmarkResult, run_dir: Path) -> None:
    """Write environment snapshot alongside measurements."""
    env_path = run_dir / "environment.json"
    env_path.write_text(
        json.dumps(result.environment_snapshot, indent=2, default=str),
        encoding="utf-8",
    )


def write_markdown(result: BenchmarkResult, output_dir: Path | None = None) -> Path:
    """Write a human-readable Markdown report."""
    out = output_dir or _default_output_dir()
    run_dir = out / result.benchmark_name / result.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "report.md"

    lines = _build_markdown(result)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _build_markdown(result: BenchmarkResult) -> list[str]:
    """Build Markdown lines from a BenchmarkResult."""
    lines: list[str] = []
    lines.append(f"# Benchmark: {result.benchmark_name}")
    lines.append("")
    lines.append(f"**Run ID:** {result.run_id}")
    lines.append(f"**Timestamp:** {result.timestamp}")
    lines.append(f"**Framework Version:** {result.engineering.framework_version}")
    lines.append("")

    lines.append("## Repository Metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    r = result.repository
    lines.append(f"| Files | {r.files} |")
    lines.append(f"| Lines of Code | {r.loc} |")
    lines.append(f"| Modules | {r.module_count} |")
    lines.append(f"| Symbols | {r.symbol_count} |")
    lines.append(f"| Functions | {r.function_count} |")
    lines.append(f"| Variables | {r.variable_count} |")
    lines.append(f"| Imports | {r.import_count} |")
    lines.append(f"| Documentation Size | {r.doc_size_bytes} bytes |")
    lines.append("")

    if result.ai:
        lines.append("## AI Metrics")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        a = result.ai
        lines.append(f"| Prompt Tokens | {a.prompt_tokens} |")
        lines.append(f"| Context Tokens | {a.context_tokens} |")
        lines.append(f"| Total Tokens Supplied | {a.total_tokens_supplied} |")
        lines.append(f"| Completion Tokens | {a.completion_tokens} |")
        lines.append(f"| Clarification Questions | {a.clarification_questions} |")
        if a.comprehension_accuracy is not None:
            lines.append(f"| Comprehension Accuracy | {a.comprehension_accuracy:.1%} |")
        if a.iterations_to_correct is not None:
            lines.append(f"| Iterations to Correct | {a.iterations_to_correct} |")
        lines.append("")

    lines.append("## Engineering Metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Execution Time | {result.engineering.execution_time_seconds:.3f}s |")
    lines.append(f"| Error Count | {result.engineering.error_count} |")
    lines.append(f"| Repeatability Hash | `{result.engineering.repeatability_hash}` |")
    lines.append("")

    if result.engineering.errors:
        lines.append("### Errors")
        for err in result.engineering.errors:
            lines.append(f"- {err}")
        lines.append("")

    lines.append("## Environment")
    lines.append("")
    env = result.environment_snapshot
    git_info = env.get("git", {})
    os_info = env.get("os", {})
    lines.append(f"- **OS:** {os_info.get('system', '')} {os_info.get('release', '')}")
    lines.append(f"- **Machine:** {os_info.get('machine', '')}")
    lines.append(f"- **Python:** {env.get('python', {}).get('version', '')}")
    lines.append(f"- **Git Commit:** `{git_info.get('commit', '')}`")
    lines.append(f"- **Git Branch:** `{git_info.get('branch', '')}`")
    lines.append(f"- **Working Tree Dirty:** {git_info.get('dirty', '')}")
    lines.append("")

    return lines


def write_summary(
    results: list[BenchmarkResult],
    output_dir: Path | None = None,
) -> Path:
    """Write a summary JSON aggregating multiple benchmark runs."""
    out = output_dir or _default_output_dir()
    out.mkdir(parents=True, exist_ok=True)
    path = out / "summary.json"

    data = {
        "total_runs": len(results),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runs": [r.to_dict() for r in results],
    }
    path.write_text(
        json.dumps(data, indent=2, default=str),
        encoding="utf-8",
    )
    return path

"""Measurement collection for benchmarks.

Three categories of metrics:
- Repository metrics: static properties of the codebase
- AI metrics: token counts, comprehension accuracy, iterations
- Engineering metrics: execution time, repeatability, errors
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# ── Repository Metrics ──────────────────────────────────────────────


@dataclass
class RepositoryMetrics:
    """Static measurements of a repository's structure."""

    files: int = 0
    loc: int = 0
    module_count: int = 0
    symbol_count: int = 0
    function_count: int = 0
    variable_count: int = 0
    import_count: int = 0
    doc_size_bytes: int = 0
    dependency_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_repo_metrics(root: Path) -> RepositoryMetrics:
    """Compute repository metrics by scanning source files."""
    metrics = RepositoryMetrics()
    ail_files = sorted(root.rglob("*.ail"))
    py_files = sorted(root.rglob("*.py"))
    all_files = ail_files + py_files

    metrics.files = len(all_files)

    for f in all_files:
        try:
            text = f.read_text(encoding="utf-8")
            lines = [l for l in text.splitlines() if l.strip()]
            metrics.loc += len(lines)
            metrics.doc_size_bytes += len(text.encode("utf-8"))
        except Exception:
            pass

    seen_modules: set[Path] = set()
    for f in ail_files:
        seen_modules.add(f.parent)
    metrics.module_count = len(seen_modules)

    for f in ail_files:
        try:
            text = f.read_text(encoding="utf-8")
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("fn "):
                    parts = stripped.split("(", 1)
                    fn_name = parts[0].removeprefix("fn ").strip()
                    if fn_name:
                        metrics.function_count += 1
                        metrics.symbol_count += 1
                elif stripped.startswith("let "):
                    var_name = stripped.removeprefix("let ").split("=", 1)[0].strip()
                    if var_name:
                        metrics.variable_count += 1
                        metrics.symbol_count += 1
                elif stripped.startswith("import "):
                    mod = stripped.removeprefix("import ").strip().rstrip(";")
                    if mod:
                        metrics.import_count += 1
        except Exception:
            pass

    metrics.dependency_count = metrics.import_count
    return metrics


# ── AI Metrics ──────────────────────────────────────────────────────


@dataclass
class AIMetrics:
    """Measurements from AI interaction with a codebase."""

    prompt_tokens: int = 0
    context_tokens: int = 0
    total_tokens_supplied: int = 0
    completion_tokens: int = 0
    clarification_questions: int = 0
    comprehension_accuracy: float | None = None  # 0.0–1.0
    first_attempt_correct: bool | None = None
    iterations_to_correct: int | None = None
    token_source_type: str = ""  # "ailang" | "python" | etc.

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── Engineering Metrics ─────────────────────────────────────────────


@dataclass
class EngineeringMetrics:
    """Measurements about the benchmark execution itself."""

    execution_time_seconds: float = 0.0
    repeatability_hash: str = ""
    error_count: int = 0
    errors: list[str] = field(default_factory=list)
    framework_version: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_repeatability_hash(data: dict[str, Any]) -> str:
    """Compute a deterministic hash of measurement data for repeatability verification."""
    raw = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


# ── Combined Benchmark Result ───────────────────────────────────────


@dataclass
class BenchmarkResult:
    """Complete, immutable measurement result for a single benchmark run."""

    benchmark_name: str
    benchmark_version: str
    run_id: str
    timestamp: str
    repository: RepositoryMetrics
    ai: AIMetrics | None
    engineering: EngineeringMetrics
    environment_snapshot: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "benchmark_name": self.benchmark_name,
            "benchmark_version": self.benchmark_version,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "repository": self.repository.to_dict(),
            "ai": self.ai.to_dict() if self.ai else None,
            "engineering": self.engineering.to_dict(),
            "environment_snapshot": self.environment_snapshot,
        }


import json  # noqa: E811 — needed inside compute_repeatability_hash

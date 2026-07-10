"""B1 — AI Repository Understanding Benchmark execution.

Measures the token cost and comprehension accuracy of AI understanding
of AILang projects. This is the measurement-only implementation;
results are not interpreted here.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from benchmarks.framework.metrics import (
    AIMetrics,
    BenchmarkResult,
    EngineeringMetrics,
    RepositoryMetrics,
)
from benchmarks.framework.reporting import generate_run_id
from benchmarks.framework.environment import snapshot, get_project_root
from benchmarks.providers.base import AIProvider


BENCHMARK_NAME = "B1 — AI Repository Understanding"
BENCHMARK_VERSION = "0.2.0"


def run(
    dataset_path: Path,
    repo_metrics: RepositoryMetrics,
    output_dir: Path | None = None,
    quiet: bool = False,
    **kwargs: Any,
) -> BenchmarkResult:
    """Execute the B1 benchmark against a dataset.

    This function:
    1. Records context structure (files, symbols, dependency graph)
    2. Estimates token cost from source text
    3. If an AI provider is given, uses its tokenizer and submits a
       comprehension prompt for measurement
    4. Records measurements without interpreting them

    Pass an AIProvider instance via the `provider` kwarg for full
    AI-integrated benchmark execution:
        from benchmarks.providers import create_provider
        provider = create_provider("openai", model="gpt-4o")
        result = run(dataset_path=..., repo_metrics=..., provider=provider)

    For manual AI interaction results, use the `ai_results` kwarg:
        ai_results = {
            "prompt_tokens": 1234,
            "context_tokens": 567,
            ...
        }
    """
    repository = repo_metrics

    ai = _measure_ai_context(dataset_path, repository, **kwargs)

    engineering = EngineeringMetrics(
        framework_version=BENCHMARK_VERSION,
    )

    run_id = generate_run_id()
    env = snapshot()

    result = BenchmarkResult(
        benchmark_name=BENCHMARK_NAME,
        benchmark_version=BENCHMARK_VERSION,
        run_id=run_id,
        timestamp=env["timestamp"],
        repository=repository,
        ai=ai,
        engineering=engineering,
        environment_snapshot=env,
    )

    return result


def _measure_ai_context(
    dataset_path: Path,
    repo_metrics: RepositoryMetrics,
    **kwargs: Any,
) -> AIMetrics:
    """Measure the AI context cost of understanding this repository.

    Three modes of operation (in priority order):
    1. If an AIProvider is given via `provider`, use its tokenizer and
       submit a comprehension prompt.
    2. If manual `ai_results` dict is given, use those values.
    3. Otherwise, use approximate token counting (4 chars ≈ 1 token).
    """
    ai = AIMetrics(
        token_source_type="ailang",
    )

    ail_files = sorted(dataset_path.rglob("*.ail"))
    source_text = ""
    for f in ail_files:
        try:
            source_text += f.read_text(encoding="utf-8") + "\n"
        except Exception:
            pass

    # Priority 1: AIProvider integration
    provider: AIProvider | None = kwargs.get("provider")
    if provider is not None:
        provider_kwargs = {k: v for k, v in kwargs.items() if k != "provider"}
        _populate_from_provider(ai, source_text, provider, **provider_kwargs)
        ai.token_source_type = f"{provider.provider_name}:{provider.model}"
        return ai

    # Priority 2: Manual AI results
    ai_results = kwargs.get("ai_results")
    if ai_results:
        _populate_from_dict(ai, ai_results)
        return ai

    # Priority 3: Approximate counting
    approx_tokens = len(source_text) // 4
    ai.context_tokens = approx_tokens
    ai.total_tokens_supplied = approx_tokens
    ai.token_source_type = "ailang_approximate"

    return ai


def _populate_from_provider(
    ai: AIMetrics,
    source_text: str,
    provider: AIProvider,
    **kwargs: Any,
) -> None:
    """Populate AIMetrics using an AIProvider for accurate measurement."""
    comprehension_prompt = kwargs.get(
        "comprehension_prompt",
        _default_comprehension_prompt(),
    )

    full_prompt = (
        f"Read this codebase and answer a question about it.\n\n"
        f"CODEBASE:\n```\n{source_text}\n```\n\n"
        f"QUESTION: {comprehension_prompt}"
    )

    result = provider.complete(full_prompt)

    ai.prompt_tokens = result.prompt_tokens_exact or result.prompt_tokens_estimated
    ai.context_tokens = result.prompt_tokens_exact or result.prompt_tokens_estimated
    ai.total_tokens_supplied = (
        (result.prompt_tokens_exact or result.prompt_tokens_estimated)
        + (result.response_tokens or 0)
    )
    ai.completion_tokens = result.response_tokens or 0
    ai.clarification_questions = result.clarification_turns


def _default_comprehension_prompt() -> str:
    return (
        "What is the primary purpose of this codebase? "
        "Answer in one sentence."
    )


def _populate_from_dict(ai: AIMetrics, data: dict[str, Any]) -> None:
    """Populate AIMetrics from a manual results dictionary."""
    ai.prompt_tokens = data.get("prompt_tokens", ai.prompt_tokens)
    ai.context_tokens = data.get("context_tokens", ai.context_tokens)
    ai.total_tokens_supplied = data.get(
        "total_tokens_supplied", ai.total_tokens_supplied
    )
    ai.completion_tokens = data.get("completion_tokens", ai.completion_tokens)
    ai.clarification_questions = data.get(
        "clarification_questions", ai.clarification_questions
    )
    ai.comprehension_accuracy = data.get("comprehension_accuracy")
    ai.first_attempt_correct = data.get("first_attempt_correct")
    ai.iterations_to_correct = data.get("iterations_to_correct")


def estimate_tokens(text: str) -> int:
    """Approximate token count for code text.

    Uses 4 chars ≈ 1 token heuristic. This is a placeholder for actual
    tokenizer integration.
    """
    return max(1, len(text) // 4)


def main() -> int:
    """Run B1 against all registered datasets.

    Usage:
        python -m benchmarks.b1_understanding.run
        python -m benchmarks.b1_understanding.run --provider openai --model gpt-4o
        python -m benchmarks.b1_understanding.run --provider local --model llama3.2
    """
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="B1 — AI Repository Understanding Benchmark"
    )
    parser.add_argument(
        "--provider", "-p",
        default=None,
        help="AI provider name (openai, anthropic, google, local)",
    )
    parser.add_argument(
        "--model", "-m",
        default="",
        help="Model identifier (provider-specific)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output",
    )

    args, _ = parser.parse_known_args()

    from benchmarks.framework.runner import run_benchmark, RunConfiguration

    datasets_dir = Path(__file__).resolve().parent.parent / "datasets"
    results_dir = Path(__file__).resolve().parent.parent / "results"

    extra = {}
    if args.provider:
        from benchmarks.providers import create_provider
        provider = create_provider(args.provider, model=args.model)
        extra["provider"] = provider
        if not args.quiet:
            print(f"Provider: {provider.provider_name} ({provider.model})")

    if not args.quiet:
        print(f"AILang Engineering Benchmark — {BENCHMARK_NAME}")
        print(f"Framework version: {BENCHMARK_VERSION}")
        print("=" * 50)
        print()

    dataset_names = sorted(
        d.name for d in datasets_dir.iterdir()
        if d.is_dir() and (d / "metadata.json").exists()
    )

    if not dataset_names:
        print("No datasets found. Run: python -m benchmarks.setup")
        return 1

    results: list[BenchmarkResult] = []

    for name in dataset_names:
        if not args.quiet:
            print(f"Dataset: {name}")
            print("-" * 30)

        config = RunConfiguration(
            benchmark_name=f"{BENCHMARK_NAME} — {name}",
            benchmark_version=BENCHMARK_VERSION,
            dataset_path=datasets_dir / name,
            output_dir=results_dir,
            quiet=args.quiet,
            extra=extra if extra else None,
        )

        result = run_benchmark(config, run)
        results.append(result)
        if not args.quiet:
            print()

    from benchmarks.framework.reporting import write_summary
    summary_path = write_summary(results, results_dir)
    if not args.quiet:
        print(f"Summary: {summary_path}")
        print("Done. Results are immutable — each run_id is unique.")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

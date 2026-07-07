# AILang Developer Experience Tool: ail benchmark
# Benchmark Runner — automated benchmark suite execution and comparison

"""AILang Benchmark Runner — executes benchmarks, measures performance,
detects regressions, and generates reports."""

from __future__ import annotations

import sys
import time
import argparse
from pathlib import Path

from tools.ail_benchmark.discovery import discover_benchmarks, discover_all_apps
from tools.ail_benchmark.runner import run_benchmark
from tools.ail_benchmark.compare import save_baseline, load_baseline, detect_regressions
from tools.ail_benchmark.reporter import generate_json_report, generate_markdown_report


def get_project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parent.parent.parent


def stats_to_dict(stats) -> dict:
    """Convert a RunStats namedtuple-like object to a dict."""
    return {
        "min": round(stats.min, 3),
        "max": round(stats.max, 3),
        "avg": round(stats.avg, 3),
        "median": round(stats.median, 3),
    }


def run_to_dict(run) -> dict:
    """Convert a BenchmarkRun to a serializable dict."""
    return {
        "build_time": round(run.build.time, 3),
        "run_time": round(run.run.time, 3),
        "exit_code": run.run.exit_code,
        "build_stdout": run.build.stdout,
        "build_stderr": run.build.stderr,
        "run_stdout": run.run.stdout,
        "run_stderr": run.run.stderr,
    }


def result_to_dict(result) -> dict:
    """Convert a BenchmarkResult to a serializable dict."""
    d = {
        "name": result.name,
        "path": result.path,
        "suite": result.suite,
        "status": result.status,
        "error": result.error,
        "runs": [run_to_dict(r) for r in result.runs],
        "stats": {
            "build_time": stats_to_dict(result.build_stats),
            "run_time": stats_to_dict(result.run_stats),
        },
    }

    # Add memory if measured
    if result.memory_kb is not None:
        d["memory_kb"] = round(result.memory_kb, 1)

    # Add regression and baseline if computed
    if hasattr(result, "_regression"):
        d["regression"] = result._regression
    else:
        d["regression"] = {
            "detected": False,
            "build_regression_pct": None,
            "run_regression_pct": None,
        }

    if hasattr(result, "_baseline"):
        d["baseline"] = result._baseline
    else:
        d["baseline"] = None

    return d


def main() -> int:
    """Main entry point for the ail benchmark tool.

    Exit codes:
        0 = All benchmarks pass, no regressions
        1 = One or more benchmarks failed (build/run error)
        2 = Performance regression detected (delta > threshold)
        3 = Internal tool error (no apps, invalid args, I/O error)
    """
    parser = argparse.ArgumentParser(
        description="AILang Benchmark Runner — execute, measure, compare"
    )
    parser.add_argument(
        "--suite",
        choices=["quick", "canonical", "full"],
        default="canonical",
        help="Benchmark suite to run (default: canonical)",
    )
    parser.add_argument(
        "--app",
        type=str,
        default=None,
        help="Run a single benchmark app by name",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=3,
        help="Number of times to repeat each benchmark (default: 3)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Per-command timeout in seconds (default: 300)",
    )
    parser.add_argument(
        "--memory",
        action="store_true",
        help="Measure peak memory usage (adds overhead)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=20.0,
        help="Regression threshold percentage (default: 20)",
    )
    parser.add_argument(
        "--baseline",
        type=str,
        default=None,
        help="Save results as baseline with this name",
    )
    parser.add_argument(
        "--compare",
        type=str,
        default=None,
        help="Compare results against a saved baseline",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output filename prefix (default: BENCHMARK_REPORT)",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output only JSON report (no Markdown)",
    )
    parser.add_argument(
        "--markdown-only",
        action="store_true",
        help="Output only Markdown report (no JSON)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-benchmark output",
    )

    args = parser.parse_args()
    root = get_project_root()
    output_prefix = args.output or "BENCHMARK_REPORT"
    start_wall = time.perf_counter()

    try:
        # Step 1: Discover benchmarks
        benchmarks = discover_benchmarks(
            root, suite=args.suite, app_name=args.app
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 3

    if not benchmarks:
        print("Error: No benchmark applications found.", file=sys.stderr)
        if args.app:
            print(
                f"  App '{args.app}' not found under apps/",
                file=sys.stderr,
            )
        elif args.suite == "full":
            print(
                "  No apps with main.ail found under apps/",
                file=sys.stderr,
            )
        else:
            print(
                f"  Suite '{args.suite}' has no valid entries. "
                "Check suite definitions in discovery.py",
                file=sys.stderr,
            )
        return 3

    if not args.quiet:
        print(f"\nAILang Benchmark Runner ({args.suite} suite)")
        print(f"  Benchmarks: {len(benchmarks)}")
        print(f"  Repeat: {args.repeat}×")
        print(f"  Memory: {'Yes' if args.memory else 'No'}")
        if args.compare:
            print(f"  Comparing against: {args.compare}")
        print()

    # Step 2: Run all benchmarks
    results = []
    for bm in benchmarks:
        if not args.quiet:
            print(f">> {bm.name} ({bm.suite})")

        try:
            result = run_benchmark(
                benchmark=bm,
                repeat=args.repeat,
                timeout=args.timeout,
                memory=args.memory,
                quiet=args.quiet,
            )
        except Exception as e:
            # Internal error during execution
            result = type(
                "BenchmarkResult",
                (),
                {
                    "name": bm.name,
                    "path": str(bm.path),
                    "suite": bm.suite,
                    "status": "fail",
                    "error": f"Internal error: {e}",
                    "runs": [],
                    "build_stats": type("s", (), {"min": 0, "max": 0, "avg": 0, "median": 0})(),
                    "run_stats": type("s", (), {"min": 0, "max": 0, "avg": 0, "median": 0})(),
                    "memory_kb": None,
                },
            )()

        results.append(result)

        if not args.quiet:
            print()

    wall_time = time.perf_counter() - start_wall

    # Step 3: Compare against baseline if requested
    if args.compare:
        baseline = load_baseline(root, args.compare)
        if baseline is None:
            print(
                f"Warning: Baseline '{args.compare}' not found. "
                "Run with --baseline to create one.",
                file=sys.stderr,
            )
        else:
            result_dicts = [result_to_dict(r) for r in results]
            detect_regressions(result_dicts, baseline, args.threshold)
            # Transfer regression info back to result objects
            for r, rd in zip(results, result_dicts):
                r._regression = rd["regression"]
                r._baseline = rd["baseline"]
        if not args.quiet:
            print(f"Compared against baseline: {args.compare}")

    # Step 4: Convert to dicts for serialization
    result_dicts = [result_to_dict(r) for r in results]

    # Re-apply regression/baseline from comparison step if they were
    # already set via the dict path above
    if args.compare and baseline is not None:
        detect_regressions(result_dicts, baseline, args.threshold)

    # Step 5: Generate reports
    json_output = generate_json_report(
        result_dicts,
        suite=args.suite,
        threshold_pct=args.threshold,
        repeat=args.repeat,
        memory=args.memory,
        timeout=args.timeout,
        baseline_name=args.compare,
    )
    md_output = generate_markdown_report(
        result_dicts,
        suite=args.suite,
        threshold_pct=args.threshold,
        repeat=args.repeat,
        memory=args.memory,
        timeout=args.timeout,
        elapsed=wall_time,
        baseline_name=args.compare,
    )

    # Step 6: Write output files
    output_dir = root / "generated" / "benchmarks"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / f"{output_prefix}.json"
    md_path = output_dir / f"{output_prefix}.md"

    if not args.markdown_only:
        json_path.write_text(json_output, encoding="utf-8")
        print(f"Generated: {json_path}")

    if not args.json_only:
        md_path.write_text(md_output, encoding="utf-8")
        print(f"Generated: {md_path}")

    # Step 7: Save baseline if requested
    if args.baseline:
        saved = save_baseline(result_dicts, root, args.baseline)
        print(f"Saved baseline: {saved}")

    # Step 8: Determine exit code (precedence: internal error > failure > regression > success)
    internal_error = False
    has_failure = False
    has_regression = False

    for r in result_dicts:
        if r.get("status") == "fail":
            has_failure = True
        reg = r.get("regression", {})
        if reg.get("detected"):
            has_regression = True

    if internal_error:
        return 3
    if has_failure:
        return 1
    if has_regression:
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

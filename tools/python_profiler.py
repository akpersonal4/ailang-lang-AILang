"""Profile AILang interpreter execution using Python cProfile.

Measures wall-clock time at the Python level for every interpreter method.
No runtime architecture changes are made — only observation.

Usage:
    python tools/python_profiler.py [apps...] [--hotspots N]
"""

from __future__ import annotations

import cProfile
import io
import pstats
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_PROJECT_ROOT = _HERE.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.runtime import builtins as runtime_builtins
from compiler.runtime.interpreter import Runtime

# =============================================================================
# 1. App definitions
# =============================================================================

AppDef = dict[str, Any]

APPS: list[AppDef] = [
    {
        "name": "dice_roller",
        "path": _PROJECT_ROOT / "apps" / "dice_roller" / "main.ail",
        "args": [],
        "description": "Rolls 20 dice, computes stats, prints histogram",
    },
    {
        "name": "hangman_game",
        "path": _PROJECT_ROOT / "apps" / "hangman_game" / "main.ail",
        "args": [],
        "description": "Auto-played hangman with random letter guessing",
    },
    {
        "name": "inventory_mgmt",
        "path": _PROJECT_ROOT / "apps" / "inventory_mgmt" / "main.ail",
        "args": [],
        "description": "Inventory management with demo data (1099 lines)",
    },
    {
        "name": "kanban",
        "path": _PROJECT_ROOT / "apps" / "kanban" / "main.ail",
        "args": [],
        "description": "Kanban board with demo sprint (1130 lines)",
    },
    {
        "name": "static_analyzer",
        "path": _PROJECT_ROOT / "apps" / "static_analyzer" / "main.ail",
        "args": [str(_PROJECT_ROOT / "apps" / "dice_roller" / "main.ail")],
        "description": "Static analyzer analyzing dice_roller (839 lines)",
    },
]


# =============================================================================
# 2. Compile + profile helpers
# =============================================================================


def compile_app(app: AppDef) -> tuple[CompilationSession | None, float]:
    """Compile an app and return (session, compile_time_sec)."""
    start = time.perf_counter()
    source_path = app["path"]
    if not source_path.exists():
        print(f"  ERROR: {source_path} not found")
        return None, 0.0

    session = CompilationSession()
    session._root = _PROJECT_ROOT
    session._resolver = type(session._resolver)(_PROJECT_ROOT)

    reporter = DiagnosticReporter()
    try:
        session.discover(source_path)
    except ValueError as e:
        print(f"  ERROR: {e}")
        return None, 0.0

    session.analyze(reporter)
    if reporter.error_count > 0:
        for diag in reporter.diagnostics:
            print(f"  COMPILE ERROR: {diag}")
        return None, 0.0

    compile_time = time.perf_counter() - start
    return session, compile_time


def collect_cache_stats(runtime: Runtime) -> dict[str, Any]:
    """Aggregate cache statistics from all environments reachable from the runtime."""
    environments: set[Any] = set()

    # Global environment
    environments.add(runtime._global_environment)

    # Module environments
    for mod_env in runtime._modules.values():
        environments.add(mod_env)

    # Walk all environments via frame stack
    for frame in runtime._frame_stack:
        e = frame.environment
        while e is not None:
            environments.add(e)
            e = e._parent  # type: ignore[attr-defined]

    total_hits = 0
    total_misses = 0
    total_negative = 0

    for env in environments:
        stats = getattr(env, "_cache_stats", None)
        if stats is not None:
            total_hits += stats.hits
            total_misses += stats.misses
            total_negative += stats.negative_hits

    total = total_hits + total_misses
    hit_rate = total_hits / total if total > 0 else 0.0

    return {
        "cache_hits": total_hits,
        "cache_misses": total_misses,
        "cache_negative_hits": total_negative,
        "cache_hit_rate": round(hit_rate, 4),
    }


def profile_app(
    session: CompilationSession,
    app: AppDef,
) -> dict[str, Any]:
    """Profile runtime execution with cProfile. Returns metrics dict."""
    bundle = session.build_ir()
    runtime_builtins._program_argv = app["args"]

    # --- Memory tracing start ---
    tracemalloc.start()

    # --- cProfile ---
    profiler = cProfile.Profile()
    profiler.enable()

    runtime_start = time.perf_counter()
    runtime = Runtime(bundle)
    for module_name in session._graph.topological_sort():
        runtime._initialize_module(module_name)

    main_module = next(
        name for name in session._graph.topological_sort() if name in bundle.module_irs
    )
    program_ir = bundle.module_irs[main_module]
    runtime.execute(program_ir)
    runtime_time = time.perf_counter() - runtime_start

    profiler.disable()

    # --- Memory ---
    _current, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # --- Cache stats ---
    cache_stats = collect_cache_stats(runtime)

    # --- Process stats ---
    sio = io.StringIO()
    stats = pstats.Stats(profiler, stream=sio).sort_stats("cumtime")
    stats.print_stats(60)

    total_fn_calls = stats.total_calls
    primitive_calls = stats.prim_calls

    hotspots_data = _extract_hotspots(stats)
    interpreter_calls = _count_interpreter_methods(stats)

    return {
        "app_name": app["name"],
        "runtime_time": round(runtime_time, 4),
        "total_calls": total_fn_calls,
        "primitive_calls": primitive_calls,
        "peak_memory_bytes": peak_memory,
        "peak_memory_mb": round(peak_memory / (1024 * 1024), 2),
        "hotspots": hotspots_data,
        "interpreter_calls": interpreter_calls,
        "cache_stats": cache_stats,
        "stats": stats,
    }


def _extract_hotspots(stats: pstats.Stats) -> list[dict[str, Any]]:
    """Extract top N hotspots from pstats data."""
    sorted_by_int = sorted(
        stats.stats.items(),
        key=lambda x: x[1][2],  # internal time
        reverse=True,
    )

    hotspots_by_int = []
    for (filename, lineno, funcname), (cc, nc, tt, ct, callers) in sorted_by_int[:40]:
        hotspots_by_int.append(
            {
                "function": funcname,
                "file": filename,
                "line": lineno,
                "calls": cc,
                "internal_time": round(tt, 4),
                "cumulative_time": round(ct, 4),
            }
        )

    return hotspots_by_int


def _count_interpreter_methods(stats: pstats.Stats) -> dict[str, Any]:
    """Sum up call counts for interpreter methods."""
    methods_of_interest = [
        "_evaluate_expression",
        "_execute_node",
        "_execute_block",
        "_call_function",
        "_resolve_name",
        "_define_local",
        "_assign_local",
        "_initialize_module",
        "_get_local",
        "execute",
        "resolve",
        "assign",
        "define",
    ]

    result: dict[str, dict[str, int | float]] = {}
    for (filename, lineno, funcname), (cc, nc, tt, ct, callers) in stats.stats.items():
        for method in methods_of_interest:
            if funcname == method or funcname.endswith(f".{method}"):
                result[funcname] = {
                    "calls": cc,
                    "internal_time": round(tt, 4),
                    "cumulative_time": round(ct, 4),
                }
                break

    return result


# =============================================================================
# 3. Reporting
# =============================================================================


def print_app_header(app: AppDef) -> None:
    print()
    print("=" * 80)
    print(f"  APP: {app['name']}")
    print(f"  File: {app['path']}")
    print(f"  Description: {app['description']}")
    print("=" * 80)


def print_metrics_table(results: list[dict[str, Any]]) -> None:
    """Print summary table of all profiled apps."""
    print()
    print("=" * 110)
    header = "  App                    Runtime(s)    PyCalls  PrimCalls PeakMem(MB)"
    has_cache = any(r.get("cache_stats", {}).get("cache_hits", 0) > 0 for r in results)
    if has_cache:
        header += "  CacheHit%"
    print(header)
    print("-" * (120 if has_cache else 100))
    for r in results:
        row = (
            f"{r['app_name']:<22} {r['runtime_time']:>10.3f} "
            f"{r['total_calls']:>10} {r['primitive_calls']:>10} "
            f"{r['peak_memory_mb']:>11.2f}"
        )
        if has_cache:
            cs = r.get("cache_stats", {})
            hr = cs.get("cache_hit_rate", 0)
            row += f" {hr:>9.1%}"
        print(row)
    print("-" * (120 if has_cache else 100))


def print_interpreter_breakdown(results: list[dict[str, Any]]) -> None:
    """Print contribution of each interpreter method to runtime."""
    print()
    print("=" * 100)
    print("  INTERPRETER METHOD BREAKDOWN (cumulative time)")
    print("=" * 100)
    for r in results:
        print(f"\n  [{r['app_name']}]  runtime={r['runtime_time']:.3f}s")
        methods = r["interpreter_calls"]
        sorted_methods = sorted(
            methods.items(),
            key=lambda x: x[1]["cumulative_time"],
            reverse=True,
        )
        if not sorted_methods:
            print("    (no interpreter methods captured)")
            continue
        header = f"  {'Method':<30} {'Calls':>10} {'Int.Time':>10} {'Cum.Time':>10} {'%Runtime':>8}"
        print(header)
        print("  " + "-" * 70)
        rt = r["runtime_time"]
        for method, data in sorted_methods:
            pct = data["cumulative_time"] / rt * 100 if rt > 0 else 0
            line = (
                f"  {method:<30} {data['calls']:>10} "
                f"{data['internal_time']:>10.4f} {data['cumulative_time']:>10.4f} "
                f"{pct:>7.1f}%"
            )
            print(line)

        # Append cache stats if available
        cs = r.get("cache_stats", {})
        if cs.get("cache_hits", 0) > 0 or cs.get("cache_misses", 0) > 0:
            print(
                f"  Cache hits: {cs['cache_hits']}, misses: {cs['cache_misses']}, "
                f"negative: {cs['cache_negative_hits']}, "
                f"hit rate: {cs['cache_hit_rate']:.1%}"
            )


def print_hotspots(results: list[dict[str, Any]], top_n: int = 15) -> None:
    """Print top-N hotspots by internal time (self time, excluding callees)."""
    print()
    print("=" * 100)
    print("  TOP HOTSPOTS BY INTERNAL TIME (self time, excluding callees)")
    print("=" * 100)
    for r in results:
        print(f"\n  [{r['app_name']}]")
        hotspots = r["hotspots"][:top_n]
        header = (
            f"  {'Rank':>4} {'Function':<40} {'Calls':>8} "
            f"{'Int.Time':>10} {'%Time':>7}"
        )
        print(header)
        print("  " + "-" * 71)
        for i, h in enumerate(hotspots):
            pct = (
                h["internal_time"] / r["runtime_time"] * 100
                if r["runtime_time"] > 0
                else 0
            )
            fn_short = h["function"][:38]
            line = (
                f"  {i+1:>4} {fn_short:<40} {h['calls']:>8} "
                f"{h['internal_time']:>10.4f} {pct:>6.2f}%"
            )
            print(line)


# =============================================================================
# 4. Main
# =============================================================================


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Python-level profiler for AILang")
    parser.add_argument(
        "apps",
        nargs="*",
        help="Apps to profile (default: all). Names: dice_roller, hangman_game, inventory_mgmt, kanban, static_analyzer",
    )
    parser.add_argument(
        "--hotspots", type=int, default=15, help="Number of hotspots to show"
    )
    args = parser.parse_args()

    if args.apps:
        app_list = [a for a in APPS if a["name"] in args.apps]
        missing = [a for a in args.apps if a not in {a2["name"] for a2 in APPS}]
        if missing:
            print(f"Unknown apps: {missing}")
            sys.exit(1)
    else:
        app_list = APPS

    results: list[dict[str, Any]] = []

    for app in app_list:
        print_app_header(app)

        # Step 1: Compile
        print("  Compiling...")
        session, compile_time = compile_app(app)
        if session is None:
            print("  SKIPPED: compilation failed")
            continue
        print(f"  Compile time: {compile_time:.3f}s")

        # Step 2: Profile runtime
        print("  Profiling runtime...")
        try:
            metrics = profile_app(session, app)
            results.append(metrics)
            print(f"  Runtime: {metrics['runtime_time']:.3f}s")
            print(
                f"  Python calls: {metrics['total_calls']} "
                f"(primitive: {metrics['primitive_calls']})"
            )
            print(f"  Peak memory: {metrics['peak_memory_mb']:.2f} MB")
            cs = metrics.get("cache_stats", {})
            if cs.get("cache_hits", 0) > 0:
                print(
                    f"  Cache: {cs['cache_hits']} hits, {cs['cache_misses']} misses, "
                    f"rate: {cs['cache_hit_rate']:.1%}"
                )
        except Exception as e:
            print(f"  RUNTIME ERROR: {e}")
            import traceback

            traceback.print_exc()
            continue

    # Reports
    print_metrics_table(results)
    print_interpreter_breakdown(results)
    print_hotspots(results, args.hotspots)

    # Save raw data
    import json

    raw = []
    for r in results:
        raw.append(
            {
                "app_name": r["app_name"],
                "runtime_time": r["runtime_time"],
                "total_calls": r["total_calls"],
                "primitive_calls": r["primitive_calls"],
                "peak_memory_bytes": r["peak_memory_bytes"],
                "peak_memory_mb": r["peak_memory_mb"],
                "hotspots_by_internal": r["hotspots"][:20],
                "interpreter_calls": r["interpreter_calls"],
                "cache_stats": r.get("cache_stats", {}),
            }
        )
    json_path = _HERE / "python_profile_data.json"
    with open(json_path, "w") as f:
        json.dump(raw, f, indent=2)
    print(f"\nRaw data saved to {json_path}")


if __name__ == "__main__":
    main()

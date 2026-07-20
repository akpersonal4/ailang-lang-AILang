"""Profile the AILang Static Code Analyzer's runtime behavior.

Instrumentes the interpreter with call counters, then runs the analyzer
against AILang programs of increasing size and records all metrics.
No runtime behaviour is modified — only observed.
"""

from __future__ import annotations

import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

# Ensure the project root is on sys.path
_HERE = Path(__file__).resolve().parent
_PROJECT_ROOT = _HERE.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.ir.nodes import (
    BlockIR,
    CallIR,
    FunctionIR,
)
from compiler.runtime.interpreter import Runtime

# =========================================================================
# 1. Instrumented Runtime (observer only, no behaviour change)
# =========================================================================


class ProfiledRuntime(Runtime):
    """Runtime that counts every interpreter operation without modifying behaviour."""

    def __init__(self, module_bundle: Any = None) -> None:
        super().__init__(module_bundle)
        self.reset_probes()

    def reset_probes(self) -> None:
        self.probe: dict[str, int] = defaultdict(int)
        self.current_depth: int = 0
        self.max_depth: int = 0
        self.depth_sum: int = 0  # sum of depths at call_entry (for avg)
        self.depth_n: int = 0  # number of depth samples

    # ---- function calls ----

    def _call_function(self, function: FunctionIR, args: tuple[Any, ...]) -> Any:
        self.probe["call_function"] += 1
        self.probe[f"call_fn:{function.name}"] += 1
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.max_depth = self.current_depth
        self.depth_sum += self.current_depth
        self.depth_n += 1
        try:
            return super()._call_function(function, args)
        finally:
            self.current_depth -= 1

    # ---- node execution dispatch ----

    def _execute_node(self, node: Any) -> Any:
        self.probe[f"exec_node:{type(node).__name__}"] += 1
        return super()._execute_node(node)

    def _execute_block(self, block: BlockIR) -> Any:
        self.probe["execute_block"] += 1
        return super()._execute_block(block)

    # ---- expression evaluation ----

    def _evaluate_expression(self, expression: Any) -> Any:
        self.probe[f"eval_expr:{type(expression).__name__}"] += 1
        if isinstance(expression, CallIR):
            self.probe[f"call_expr:{expression.callee}"] += 1
        return super()._evaluate_expression(expression)

    # ---- name resolution ----

    def _resolve_name(self, name: str) -> Any:
        self.probe[f"resolve:{name}"] += 1
        return super()._resolve_name(name)


# =========================================================================
# 2. Test program generator
# =========================================================================


def generate_test_program(target_lines: int) -> str:
    """Generate a valid AILang program with approximately *target_lines* lines.

    Each function is ~4 lines of body plus the definition line (5 total).
    The main function collects results from a subset of functions.
    """
    # Fixed overhead: main function (~5 lines) + closing
    overhead = 5
    body_lines = max(target_lines - overhead, 1)
    # Estimate: each function is ~6 lines (def, let x=..., let y=..., return, blank)
    approx_fn_lines = 6
    n_fns = max(body_lines // approx_fn_lines, 1)
    actual_fn_lines = n_fns * approx_fn_lines
    # Pad with extra let decls in main to reach target
    extra_decls = max(target_lines - overhead - actual_fn_lines, 0)

    lines: list[str] = ["import string;", "import convert;", ""]

    for i in range(n_fns):
        lines.append(f"fn fn_{i}(x) {{")
        lines.append(f"    let y = x + {i};")
        lines.append('    let z = string.uppercase("a");')
        lines.append("    return y;")
        lines.append("}")
        lines.append("")

    # main function
    lines.append("fn main() {")
    # call some functions
    calls = min(n_fns, 20)
    result_var = "r"
    for i in range(calls):
        if i == 0:
            lines.append(f"    let r = fn_{i}({i});")
        else:
            lines.append(f"    r = fn_{i}(r);")
    for i in range(calls, n_fns):
        lines.append(f"    let t{i} = fn_{i}(0);")
    # extra padding
    for i in range(extra_decls):
        lines.append(f"    let pad{i} = {i};")
    lines.append("    return 0;")
    lines.append("}")

    return "\n".join(lines)


# =========================================================================
# 3. Compile + run helper
# =========================================================================


def compile_and_profile_analyzer(
    analyzer_path: Path,
    test_file_source: str,
) -> ProfiledRuntime:
    """Compile the analyzer together with a test file, then execute and profile."""

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Write the test file
        test_file_path = tmp / "test_input.ail"
        test_file_path.write_text(test_file_source, encoding="utf-8")

        # Compile the analyzer (which imports test_input.ail as an arg)
        # Actually the analyzer takes environment.args() — we supply test file path
        session = CompilationSession()
        session._root = _PROJECT_ROOT
        session._resolver = type(session._resolver)(_PROJECT_ROOT)
        session.discover(analyzer_path)

        reporter = DiagnosticReporter()
        session.analyze(reporter)
        if reporter.error_count > 0:
            for err in reporter.errors:
                print(f"  COMPILE ERROR: {err}")
            raise RuntimeError(f"Compilation failed with {reporter.error_count} errors")

        bundle = session.build_ir()

        # Create profiled runtime
        runtime = ProfiledRuntime(bundle)

        # Inject test file path into environment args
        import compiler.runtime.builtins as builtins_mod

        builtins_mod._program_argv = [str(test_file_path)]

        # --- Runtime execution starts here ---
        runtime_start = time.perf_counter()

        # Initialize all modules (stdlib + analyzer)
        for module_name in session._graph.topological_sort():
            runtime._initialize_module(module_name)

        # Execute the analyzer's main function
        entry_module = next(name for name in bundle.module_irs if name.endswith("main"))
        runtime.execute(bundle.module_irs[entry_module])

        runtime_elapsed = time.perf_counter() - runtime_start
        runtime._runtime_elapsed = runtime_elapsed

        return runtime


# =========================================================================
# 4. Reporting helpers
# =========================================================================


def collect_metrics(
    probe: dict[str, int],
    max_depth: int,
    depth_sum: int,
    depth_n: int,
    elapsed: float,
    runtime_elapsed: float,
    lines: int,
) -> dict:
    """Extract structured metrics from raw probe data."""
    # Aggregate by category
    exec_node_total = sum(v for k, v in probe.items() if k.startswith("exec_node:"))
    eval_expr_total = sum(v for k, v in probe.items() if k.startswith("eval_expr:"))
    call_expr_total = sum(v for k, v in probe.items() if k.startswith("call_expr:"))
    resolve_total = sum(v for k, v in probe.items() if k.startswith("resolve:"))

    fn_calls = probe.get("call_function", 0)
    exec_blocks = probe.get("execute_block", 0)

    # Count specific operations
    call_expr_by_name = {
        k.replace("call_expr:", ""): v
        for k, v in probe.items()
        if k.startswith("call_expr:")
    }
    call_fn_by_name = {
        k.replace("call_fn:", ""): v
        for k, v in probe.items()
        if k.startswith("call_fn:")
    }
    exec_node_by_type = {
        k.replace("exec_node:", ""): v
        for k, v in probe.items()
        if k.startswith("exec_node:")
    }
    eval_expr_by_type = {
        k.replace("eval_expr:", ""): v
        for k, v in probe.items()
        if k.startswith("eval_expr:")
    }

    # String, list, map operation counts
    string_substring = call_expr_by_name.get("string_substring", 0)
    string_len = call_fn_by_name.get("string.length", 0)
    string_equals = call_fn_by_name.get("string.equals", 0)
    list_get = call_fn_by_name.get("list.get", 0)
    list_append = call_fn_by_name.get("list.append", 0)
    list_len = call_fn_by_name.get("list.len", 0)
    list_contains = call_fn_by_name.get("list.contains", 0)
    map_get = call_fn_by_name.get("map.get", 0)
    map_has = call_fn_by_name.get("map.has", 0)
    map_set = call_fn_by_name.get("map.set", 0)
    map_keys = call_fn_by_name.get("map.keys", 0)
    convert_to_string = call_fn_by_name.get("convert.to_string", 0)
    find_substring = call_fn_by_name.get("find_substring", 0)
    string_uppercase = call_fn_by_name.get("string.uppercase", 0)
    io_writeln = call_fn_by_name.get("io.writeln", 0)

    avg_depth = depth_sum / depth_n if depth_n > 0 else 0

    # Top 10 call targets
    top_calls = sorted(call_fn_by_name.items(), key=lambda x: -x[1])[:10]

    return {
        "target_lines": lines,
        "elapsed_sec": round(elapsed, 3),
        "runtime_sec": round(runtime_elapsed, 3),
        "fn_calls": fn_calls,
        "exec_blocks": exec_blocks,
        "exec_node_total": exec_node_total,
        "eval_expr_total": eval_expr_total,
        "call_expr_total": call_expr_total,
        "resolve_total": resolve_total,
        "max_depth": max_depth,
        "avg_depth": round(avg_depth, 2),
        "string_substring": string_substring,
        "string_len": string_len,
        "string_equals": string_equals,
        "list_get": list_get,
        "list_append": list_append,
        "list_len": list_len,
        "list_contains": list_contains,
        "map_get": map_get,
        "map_has": map_has,
        "map_set": map_set,
        "map_keys": map_keys,
        "convert_to_string": convert_to_string,
        "find_substring": find_substring,
        "string_uppercase": string_uppercase,
        "io_writeln": io_writeln,
        "top_calls": top_calls,
        "exec_node_by_type": exec_node_by_type,
        "eval_expr_by_type": eval_expr_by_type,
        "call_fn_by_name": call_fn_by_name,
    }


def print_metrics_table(results: list[dict]) -> None:
    """Print a compact summary table."""
    print()
    print("=" * 100)
    print("  SCALING PROFILE SUMMARY")
    print("=" * 100)
    header = (
        f"{'Lines':>6} {'RunTime':>8} {'FnCalls':>10} {'MaxDepth':>9} {'AvgDepth':>9} "
    )
    header += f"{'ExecNode':>10} {'EvalExpr':>9} {'Resolve':>9} "
    header += f"{'str.substr':>10} {'list.get':>9} {'map.get/has':>11}"
    print(header)
    print("-" * 100)
    for r in results:
        row = f"{r['target_lines']:>6} {r['runtime_sec']:>8.3f} {r['fn_calls']:>10} "
        row += f"{r['max_depth']:>9} {r['avg_depth']:>9.2f} "
        row += f"{r['exec_node_total']:>10} {r['eval_expr_total']:>9} {r['resolve_total']:>9} "
        row += f"{r['string_substring']:>10} {r['list_get']:>9} {r['map_get'] + r['map_has']:>11}"
        print(row)
    print("-" * 100)


def print_top_calls_table(results: list[dict]) -> None:
    """Print top 10 most-called functions per file size."""
    print()
    print("=" * 100)
    print("  TOP-10 MOST CALLED FUNCTIONS (by target file size)")
    print("=" * 100)
    for r in results:
        print(f"\n  [{r['target_lines']} lines]")
        for i, (name, count) in enumerate(r["top_calls"]):
            print(f"    {i+1:>2}. {name:<35} {count:>8}")


def print_hotspot_breakdown(results: list[dict]) -> None:
    """Estimate percentage of time spent in each operation category."""
    print()
    print("=" * 80)
    print("  HOTSPOT BREAKDOWN (largest file)")
    print("=" * 80)
    r = results[-1]  # largest file
    total_ops = r["exec_node_total"]
    if total_ops == 0:
        return

    categories = defaultdict(int)
    for node_type, count in r["exec_node_by_type"].items():
        categories["exec_node:" + node_type] = count
    for expr_type, count in r["eval_expr_by_type"].items():
        categories["eval_expr:" + expr_type] = count
    categories["call_function"] = r["fn_calls"]
    categories["execute_block"] = r["exec_blocks"]

    sorted_items = sorted(categories.items(), key=lambda x: -x[1])
    total = sum(v for _, v in sorted_items)

    print(f"\n  Total instrumented operations: {total}")
    print(f"  Runtime time: {r['runtime_sec']:.3f}s")
    print(f"  Operations/sec: {total / r['runtime_sec']:.0f}")
    print()
    print(f"  {'Rank':>4} {'Operation':<45} {'Count':>10} {'%':>7}")
    print("  " + "-" * 68)
    for i, (op, count) in enumerate(sorted_items[:15]):
        pct = count / total * 100
        print(f"  {i+1:>4} {op:<45} {count:>10} {pct:>6.2f}%")
    print()

    # Time attribution (crude: each operation has equal cost)
    ops_per_sec = total / r["runtime_sec"]
    print("  Crude time attribution (assuming equal cost per operation):")
    print(f"  {'Operation':<45} {'Count':>10} {'Est. Time(s)':>13} {'%':>7}")
    print("  " + "-" * 77)
    for i, (op, count) in enumerate(sorted_items[:10]):
        est_time = count / ops_per_sec
        pct = count / total * 100
        print(f"  {op:<45} {count:>10} {est_time:>13.3f} {pct:>6.2f}%")


# =========================================================================
# 5. Main
# =========================================================================


def main() -> None:
    import sys

    if len(sys.argv) > 1:
        SIZES = [int(s) for s in sys.argv[1:]]
    else:
        SIZES = [25, 50, 100, 250, 500, 1000]
    analyzer_path = _PROJECT_ROOT / "apps" / "static_analyzer" / "main.ail"

    print(f"Project root: {_PROJECT_ROOT}")
    print(f"Analyzer:     {analyzer_path}")
    print(f"Target sizes: {SIZES}")

    results = []

    for size in SIZES:
        print(f"\n--- Generating {size}-line test program ---")
        source = generate_test_program(size)
        actual_lines = source.count("\n") + 1
        print(f"    Generated {actual_lines} lines (target {size})")

        print("    Compiling and profiling...")
        start = time.perf_counter()
        try:
            runtime = compile_and_profile_analyzer(analyzer_path, source)
            elapsed = time.perf_counter() - start

            metrics = collect_metrics(
                runtime.probe,
                runtime.max_depth,
                runtime.depth_sum,
                runtime.depth_n,
                elapsed,
                runtime._runtime_elapsed,
                actual_lines,
            )
            results.append(metrics)

            print(
                f"    Done in {elapsed:.3f}s total, runtime: {runtime._runtime_elapsed:.3f}s"
            )
            print(
                f"    AILang fn calls: {metrics['fn_calls']}, "
                f"max depth: {metrics['max_depth']}, "
                f"exec nodes: {metrics['exec_node_total']}"
            )

            # Save partial results after each run
            import json

            partial_path = _HERE / f"profile_{actual_lines}.json"
            with open(partial_path, "w") as fp:
                json.dump(metrics, fp, indent=2, default=str)
            print(f"    Saved partial data to {partial_path}")

        except Exception as e:
            print(f"    FAILED: {e}")
            import traceback

            traceback.print_exc()
            # Write the generated source for debugging
            debug_path = _HERE / f"debug_{size}.ail"
            debug_path.write_text(source)
            print(f"    Saved debug source to {debug_path}")
            continue

    # Print reports
    print_metrics_table(results)
    print_top_calls_table(results)
    print_hotspot_breakdown(results)

    # Write raw data to JSON for further analysis
    import json

    report = {
        "sizes_tested": SIZES,
        "results": results,
    }
    json_path = _HERE / "profile_data.json"
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nRaw data saved to {json_path}")


if __name__ == "__main__":
    main()

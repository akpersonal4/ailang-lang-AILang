"""A101 post-ADR-018 validation: canonical 10k perf (x5) + determinism SHA256.

Mirrors benchmarks/phase2_trampoline_validation.py::_compile_and_run exactly.
ADR-017 baseline (section 19.2): 980.33 ms avg (3 runs).
"""
from __future__ import annotations

import hashlib
import statistics
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.runtime.interpreter import Runtime

CANONICAL_SOURCE = """
import list;
import map;
import string;
import convert;

fn process_rows(items, idx, acc_sum, acc_max, acc_count) {
    if (idx >= list.len(items)) {
        return acc_sum + acc_max * 10000 + acc_count;
    }
    let row = list.get(items, idx);
    let amount = map.get(row, "amount");
    let new_sum = acc_sum + amount;
    let new_count = acc_count + 1;
    if (amount > acc_max) {
        return process_rows(items, idx + 1, new_sum, amount, new_count);
    }
    return process_rows(items, idx + 1, new_sum, acc_max, new_count);
}

fn build_records(n, items) {
    if (n <= 0) {
        return items;
    }
    let record = map.new();
    map.set(record, "id", n);
    map.set(record, "amount", n * 3);
    list.append(items, record);
    return build_records(n - 1, items);
}

fn main() {
    let items = list.new();
    let all_items = build_records(10000, items);
    let result = process_rows(all_items, 0, 0, 0, 0);
    return result;
}
"""


def compile_once(source: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        main_file = Path(tmpdir) / "main.ail"
        main_file.write_text(source)
        session = CompilationSession()
        session._root = REPO_ROOT
        session._resolver = type(session._resolver)(REPO_ROOT)
        session.discover(main_file)
        reporter = DiagnosticReporter()
        session.analyze(reporter)
        assert reporter.error_count == 0
        bundle = session.build_ir()
        runtime = Runtime(bundle)
        for module_name in session._graph.topological_sort():
            runtime._initialize_module(module_name)
        entry = next(n for n in bundle.module_irs if n.endswith("main"))
        return runtime, bundle.module_irs[entry]


def main() -> None:
    RUNS = 5
    times_ms, results, hashes = [], [], []
    for i in range(RUNS):
        runtime, entry = compile_once(CANONICAL_SOURCE)
        start = time.perf_counter()
        result = int(runtime.execute(entry))
        elapsed_ms = (time.perf_counter() - start) * 1000
        out = str(result)
        times_ms.append(elapsed_ms)
        results.append(result)
        hashes.append(hashlib.sha256(out.encode()).hexdigest())
        print(f"Run {i+1}: {elapsed_ms:.2f} ms  result={result}  sha256={hashes[-1]}")

    baseline = 980.33
    avg = statistics.mean(times_ms)
    stdev = statistics.stdev(times_ms)
    variance = statistics.variance(times_ms)
    print("\n--- Performance vs ADR-017 baseline ---")
    print(f"Runs          : {RUNS}")
    print(f"Average       : {avg:.2f} ms")
    print(f"Min / Max     : {min(times_ms):.2f} / {max(times_ms):.2f} ms")
    print(f"Stdev         : {stdev:.2f} ms")
    print(f"Variance      : {variance:.2f} ms^2")
    print(f"ADR-017 base  : {baseline:.2f} ms (avg, section 19.2)")
    delta = avg - baseline
    pct = delta / baseline * 100
    print(f"Change        : {delta:+.2f} ms ({pct:+.2f}%)")
    print(f"Target <5000ms: {'PASS' if avg < 5000 else 'FAIL'}")

    print("\n--- Determinism ---")
    distinct_results = len(set(results))
    distinct_hashes = len(set(hashes))
    print(f"Distinct results : {distinct_results} (expected 1)")
    print(f"Distinct SHA256  : {distinct_hashes} (expected 1)")
    print(f"All identical    : {distinct_hashes == 1 and distinct_results == 1}")
    print(f"Expected value   : 450025000 -> {'MATCH' if results[0] == 450025000 else 'MISMATCH'}")


if __name__ == "__main__":
    main()

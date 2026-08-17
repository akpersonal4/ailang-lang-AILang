"""Bounded Phase-0 performance pre-measurement driver.

Purpose
-------
Inform Gate F (iteration-model decision) BEFORE any trampoline/loop work by
measuring what is runnable at 10k TODAY on the working-tree interpreter:

  A. COMPILE scaling   - lex/parse/analyze/typecheck/build_ir of a source with
                         N data records (no runtime). Measures compiler
                         throughput at business-data volume.
  B. NATIVE-STDLIB rt  - execute a CSV load + stringify workload that uses only
                         native stdlib ops (no AILang recursion), so it runs at
                         10k without hitting the 2000-recursion ceiling.
  C. RECURSION probe   - a pure-AILang recursive depth driver: documents
                         per-depth scaling (post-P1b _frame_ever_bound) and
                         empirically locates the recursion ceiling.

Important caveats (per AILang baseline discipline / no-chat-memory rules):
- This measures the WORKING TREE (commit 837e05c "v1.1.19" + uncommitted
  P0-1/P0-2 changes). It is NOT the published PyPI wheel.
- "Compile excluded" for runtime numbers: each program is compiled once and
  only `Runtime.execute` is timed (like the M137 methodology).
- Values are min-of-N in-process runs, not a statistically rigorous study.

Usage (from repo root, system python has working-tree `compiler` on path):
    python benchmarks/perf_scaling_pre_iteration.py
"""

from __future__ import annotations

import gc
import sys
import tempfile
import time
from pathlib import Path

# Force the working-tree `compiler` package onto sys.path regardless of how this
# script is invoked. When run as a plain script (`python benchmarks/xxx.py`)
# sys.path[0] is the `benchmarks/` dir, so without this the *installed* AILang
# package would be imported instead of the working tree being measured.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from compiler.runtime.sandbox import SandboxPolicy, set_policy


# ---------------------------------------------------------------------------
# Workload generators (valid AILang syntax verified against apps/ + stdlib/)
# ---------------------------------------------------------------------------


def gen_compile_source(n: int) -> str:
    """N top-level bindings + main -> scales lexer/parser/semantic/type/IR."""
    lines: list[str] = []
    for i in range(n):
        lines.append(f"let v_{i} = {i};")
    lines.append(f"fn main() {{ return v_{n - 1} }}")
    return "\n".join(lines)


def gen_native_source(n: int) -> str:
    """CSV string of N rows; parse + stringify all native (no AILang recursion)."""
    rows = ["id,amt"]
    for i in range(1, n + 1):
        rows.append(f"{i},{'%.2f' % (i * 0.5)}")
    csv_text = "\\n".join(rows)
    return (
        "import csv;\n"
        "import list;\n"
        f'let data = "{csv_text}";\n'
        "fn main() {\n"
        "    let rows = csv.parse(data);\n"
        "    let count = list.len(rows);\n"
        "    let out = csv.stringify(rows);\n"
        "    return count\n"
        "}"
    )


def gen_recurse_source(d: int) -> str:
    return (
        "fn dec(n) {\n"
        "    if (n <= 0) { return 0 }\n"
        "    return dec(n - 1) + 1\n"
        "}\n"
        f"fn main() {{ return dec({d}) }}"
    )


# ---------------------------------------------------------------------------
# Measurement helpers
# ---------------------------------------------------------------------------


def measure_compile(src_path: Path, reps: int = 3) -> float:
    """Compile-only: lex->parse->analyze->typecheck->build_ir. Returns min ms."""
    from compiler.cli.main import _compile

    set_policy(SandboxPolicy(enabled=False))
    times: list[float] = []
    for _ in range(reps):
        gc.collect()
        t0 = time.perf_counter()
        session, reporter = _compile(src_path, quiet=True)
        assert session is not None, "compile failed"
        session.build_ir()
        times.append((time.perf_counter() - t0) * 1000.0)
    return min(times)


def _run_once(src_path: Path) -> float:
    """Full setup + Runtime.execute, returns wall ms for execute only."""
    from compiler.cli.main import _compile
    from compiler.runtime import Runtime

    set_policy(SandboxPolicy(enabled=False))
    session, _ = _compile(src_path, quiet=True)
    assert session is not None, "compile failed"
    bundle = session.build_ir()

    # sandbox disabled by default policy above; keep consistent
    runtime = Runtime(bundle)
    source_map: dict[str, tuple[str, str]] = {}
    for module_name, src in session._sources.items():
        source_map[module_name] = (str(src.path), src.text)
    runtime.set_source_map(source_map)

    entry_module = session._path_to_module_name(src_path)
    if entry_module not in bundle.module_irs:
        for module_name in session._graph.topological_sort():
            if module_name in bundle.module_irs:
                entry_module = module_name
                break

    for module_name in session._graph.topological_sort():
        if module_name == entry_module:
            continue
        runtime._initialize_module(module_name)
    runtime._initialize_module(entry_module, run_body=False)

    program_ir = bundle.module_irs[entry_module]
    gc.collect()
    t0 = time.perf_counter()
    runtime.execute(program_ir)
    return (time.perf_counter() - t0) * 1000.0


def measure_runtime(src_path: Path, reps: int = 3) -> float:
    """Compile once; time Runtime.execute (compile excluded). Returns min ms."""
    times: list[float] = []
    for _ in range(reps):
        times.append(_run_once(src_path))
    return min(times)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main() -> None:
    work = Path(tempfile.mkdtemp(prefix="ail_perf_pre_"))
    print(f"scratch dir: {work}")

    n_compile = [100, 200, 400, 800, 1000, 2000, 5000, 10000]
    n_native = [100, 200, 400, 800, 1000, 2000, 5000, 10000]
    d_recurse = [100, 200, 400, 800, 1000, 1500, 1999, 2000, 2001, 3000]

    print("\n=== A. COMPILE SCALING (ms; LOC/s; min of 3) ===")
    print("N\tms\tLOC/s")
    for n in n_compile:
        p = work / f"com_{n}.ail"
        p.write_text(gen_compile_source(n), encoding="utf-8")
        ms = measure_compile(p)
        print(f"{n}\t{ms:.1f}\t{n / (ms / 1000.0):,.0f}")

    print("\n=== B. NATIVE-STDLIB RUNTIME (ms, compile excluded; min of 3) ===")
    print("N\tms")
    for n in n_native:
        p = work / f"nat_{n}.ail"
        p.write_text(gen_native_source(n), encoding="utf-8")
        ms = measure_runtime(p)
        print(f"{n}\t{ms:.1f}")

    print("\n=== C. RECURSION DEPTH PROBE (ms, compile excluded; min of 3) ===")
    print("depth\tms\tstatus")
    for d in d_recurse:
        p = work / f"rec_{d}.ail"
        p.write_text(gen_recurse_source(d), encoding="utf-8")
        # compile once to validate syntax
        from compiler.cli.main import _compile

        session, _ = _compile(p, quiet=True)
        if session is None:
            print(f"{d}\t-\tCOMPILE_FAIL")
            continue
        try:
            ms = measure_runtime(p)
            print(f"{d}\t{ms:.2f}\tOK")
        except Exception as exc:  # expected: recursion-ceiling RuntimeError
            print(f"{d}\t-\tFAIL ({type(exc).__name__}: {exc})")


if __name__ == "__main__":
    main()


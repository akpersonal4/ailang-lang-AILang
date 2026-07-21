"""Benchmark suite for AILang compiler and runtime.

Measures compile time, execution time, determinism, and memory usage
across programs of varying size and complexity.
"""

from __future__ import annotations

import time
import tracemalloc
from pathlib import Path

import pytest

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.runtime.interpreter import Runtime

BENCHMARK_THRESHOLD_WARNING = (
    "Benchmarks are machine-dependent. Failures indicate regression >2x "
    "from baseline, not absolute performance."
)

# =============================================================================
# Helpers
# =============================================================================


def _compile_ail_source(source: str, repo_root: Path) -> CompilationSession:
    """Compile AILang source and return the session."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

        session = CompilationSession()
        session._root = repo_root
        session._resolver = type(session._resolver)(repo_root)
        session.discover(main_file)

        reporter = DiagnosticReporter()
        session.analyze(reporter)
        assert reporter.error_count == 0

        return session


def _compile_and_run(source: str) -> int:
    """Full compile + run, return main() result."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

        repo_root = Path(__file__).resolve().parents[1]
        session = CompilationSession()
        session._root = repo_root
        session._resolver = type(session._resolver)(repo_root)
        session.discover(main_file)

        reporter = DiagnosticReporter()
        session.analyze(reporter)
        assert reporter.error_count == 0

        bundle = session.build_ir()
        runtime = Runtime(bundle)
        for module_name in session._graph.topological_sort():
            runtime._initialize_module(module_name)

        entry_module = next(name for name in bundle.module_irs if name.endswith("main"))
        return int(runtime.execute(bundle.module_irs[entry_module]))


# =============================================================================
# Determinism Verification
# =============================================================================


class TestDeterminism:
    """Every program must produce the same result across multiple runs."""

    PROGRAMS: list[tuple[str, str, int]] = [
        (
            "arithmetic",
            """
fn main() {
    let x = (1 + 2) * 3 - 4 / 2;
    return x;
}
""",
            7,  # (3*3) - 2 = 7
        ),
        (
            "recursion",
            """
fn fib(n) {
    if (n == 0) { return 0; }
    if (n == 1) { return 1; }
    return fib(n - 1) + fib(n - 2);
}
fn main() {
    return fib(10);
}
""",
            55,
        ),
        (
            "stdlib_string",
            """
import string;
fn main() {
    let s = string.uppercase(string.trim("  hello  "));
    if (s == "HELLO") {
        return 1;
    }
    return 0;
}
""",
            1,
        ),
        (
            "stdlib_json",
            """
import json;
import map;
fn main() {
    let data = json.parse("{\\"a\\": 1}");
    let v = map.get(data, "a");
    if (v == 1) {
        return 1;
    }
    return 0;
}
""",
            1,
        ),
        (
            "stdlib_list",
            """
import list;
fn main() {
    let items = list.new();
    list.append(items, 10);
    list.append(items, 20);
    let sum = list.get(items, 0) + list.get(items, 1);
    if (sum == 30) {
        return 1;
    }
    return 0;
}
""",
            1,
        ),
    ]

    RUNS = 5

    @pytest.mark.parametrize("name,source,expected", PROGRAMS)
    def test_deterministic(self, name: str, source: str, expected: int) -> None:
        """Program produces same result on every run."""
        results: list[int] = []
        for _ in range(self.RUNS):
            results.append(_compile_and_run(source))
        for r in results:
            assert r == expected, (
                f"Non-deterministic result in '{name}': "
                f"expected {expected}, got {r} across {results}"
            )


# =============================================================================
# Compile Time Benchmarks
# =============================================================================


class TestCompileTimeBenchmarks:
    """Measure compile time for programs of increasing size."""

    def _benchmark_compile(self, source: str) -> float:
        """Return compile time in seconds."""
        repo_root = Path(__file__).resolve().parents[1]
        start = time.perf_counter()
        _compile_ail_source(source, repo_root)
        return time.perf_counter() - start

    def test_compile_time_small(self) -> None:
        """Small program (<10 LOC) compiles quickly."""
        source = """
fn main() {
    return 42;
}
"""
        elapsed = self._benchmark_compile(source)
        assert elapsed < 5.0, f"Small program compile took {elapsed:.3f}s (>5s)"

    def test_compile_time_medium(self) -> None:
        """Medium program (stdlib imports, ~30 LOC) compiles in reasonable time."""
        source = """
import json;
import list;
import map;
import string;
import math;

fn process(items) {
    let first = list.get(items, 0);
    let upper = string.uppercase(first);
    return upper;
}

fn main() {
    let data = json.parse("{\\"values\\": [\\"hello\\", \\"world\\"]}");
    let items = list.new();
    list.append(items, "a");
    list.append(items, "b");
    let r = process(items);
    let m = math.add(1, 2);
    if (r == "A") {
        return 1;
    }
    return 0;
}
"""
        elapsed = self._benchmark_compile(source)
        assert elapsed < 10.0, f"Medium program compile took {elapsed:.3f}s (>10s)"

    def test_compile_time_large_recursive(self) -> None:
        """Large recursive program (~50 LOC) compiles in reasonable time."""
        source = """
fn ack(m, n) {
    if (m == 0) {
        return n + 1;
    }
    if (n == 0) {
        return ack(m - 1, 1);
    }
    return ack(m - 1, ack(m, n - 1));
}

fn fib(n) {
    if (n <= 1) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

fn gcd(a, b) {
    if (b == 0) {
        return a;
    }
    return gcd(b, a % b);
}

fn sum(n) {
    if (n == 0) {
        return 0;
    }
    return n + sum(n - 1);
}

fn main() {
    let f = fib(10);
    let g = gcd(48, 18);
    let s = sum(100);
    if (f == 55 && g == 6) {
        return 1;
    }
    return 0;
}
"""
        elapsed = self._benchmark_compile(source)
        assert elapsed < 15.0, f"Large program compile took {elapsed:.3f}s (>15s)"


# =============================================================================
# Runtime Benchmarks
# =============================================================================


class TestRuntimeBenchmarks:
    """Measure execution time for programs of varying complexity."""

    def _benchmark_runtime(self, source: str) -> tuple[float, int]:
        """Return (execution time in seconds, result)."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            main_file = tmp_path / "main.ail"
            main_file.write_text(source)

            repo_root = Path(__file__).resolve().parents[1]
            session = CompilationSession()
            session._root = repo_root
            session._resolver = type(session._resolver)(repo_root)
            session.discover(main_file)

            reporter = DiagnosticReporter()
            session.analyze(reporter)
            assert reporter.error_count == 0

            bundle = session.build_ir()
            runtime = Runtime(bundle)
            for module_name in session._graph.topological_sort():
                runtime._initialize_module(module_name)

            entry_module = next(
                name for name in bundle.module_irs if name.endswith("main")
            )
            start = time.perf_counter()
            result = int(runtime.execute(bundle.module_irs[entry_module]))
            elapsed = time.perf_counter() - start
            return elapsed, result

    def test_runtime_trivial(self) -> None:
        """Trivial program executes quickly."""
        elapsed, result = self._benchmark_runtime("""
fn main() {
    return 1;
}
""")
        assert result == 1
        assert elapsed < 5.0, f"Trivial runtime took {elapsed:.3f}s (>5s)"

    def test_runtime_fibonacci_15(self) -> None:
        """Fibonacci(15) completes in reasonable time."""
        elapsed, result = self._benchmark_runtime("""
fn fib(n) {
    if (n <= 1) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}
fn main() {
    return fib(15);
}
""")
        assert result == 610
        assert elapsed < 10.0, f"fib(15) took {elapsed:.3f}s (>10s)"

    def test_runtime_nested_recursion(self) -> None:
        """Nested recursive calls (ackermann) complete without overflow."""
        elapsed, result = self._benchmark_runtime("""
fn ack(m, n) {
    if (m == 0) {
        return n + 1;
    }
    if (n == 0) {
        return ack(m - 1, 1);
    }
    return ack(m - 1, ack(m, n - 1));
}
fn main() {
    return ack(3, 4);
}
""")
        assert result == 125
        assert elapsed < 30.0, f"ack(3,4) took {elapsed:.3f}s (>30s)"


# =============================================================================
# Memory Usage Benchmarks
# =============================================================================


class TestMemoryBenchmarks:
    """Memory usage during compilation and execution."""

    def test_compile_memory_small(self) -> None:
        """Memory usage for small program is bounded."""
        source = """
fn main() {
    return 42;
}
"""
        repo_root = Path(__file__).resolve().parents[1]
        tracemalloc.start()
        try:
            _compile_ail_source(source, repo_root)
            _current, peak = tracemalloc.get_traced_memory()
            peak_mb = peak / (1024 * 1024)
            assert peak_mb < 200, f"Peak memory {peak_mb:.1f}MB (>200MB)"
        finally:
            tracemalloc.stop()

    def test_memory_stdlib_program(self) -> None:
        """Memory usage for stdlib-importing program is bounded."""
        source = """
import json;
import csv;
import list;
import map;
import string;

fn main() {
    let data = json.parse("{\\"items\\": [1, 2, 3]}");
    let csv_data = csv.parse("a,b\\n1,2");
    let s = string.uppercase("hello");
    return 1;
}
"""
        repo_root = Path(__file__).resolve().parents[1]
        tracemalloc.start()
        try:
            session = _compile_ail_source(source, repo_root)
            bundle = session.build_ir()
            runtime = Runtime(bundle)
            for module_name in session._graph.topological_sort():
                runtime._initialize_module(module_name)

            entry_module = next(
                name for name in bundle.module_irs if name.endswith("main")
            )
            runtime.execute(bundle.module_irs[entry_module])

            _current, peak = tracemalloc.get_traced_memory()
            peak_mb = peak / (1024 * 1024)
            assert peak_mb < 300, f"Peak memory {peak_mb:.1f}MB (>300MB)"
        finally:
            tracemalloc.stop()


# =============================================================================
# End-to-end Pipeline Benchmark
# =============================================================================


def test_full_pipeline_small_program() -> None:
    """End-to-end compile+run for a small program is under 10s."""
    source = """
fn main() {
    return 42;
}
"""
    start = time.perf_counter()
    result = _compile_and_run(source)
    elapsed = time.perf_counter() - start

    assert result == 42
    assert elapsed < 10.0, f"Full pipeline took {elapsed:.3f}s (>10s)"


# =============================================================================
# LOC-based Compile Time Benchmarks
# =============================================================================


class TestCompileTimeByLOC:
    """Measure compile time for programs of specific LOC sizes."""

    LOC_PROGRAMS: list[tuple[str, int, int]] = [
        ("100_loc", 100, 10.0),
        ("500_loc", 500, 20.0),
        ("1000_loc", 1000, 30.0),
        ("5000_loc", 5000, 60.0),
    ]

    def _generate_loc_program(self, loc: int) -> str:
        lines = ["fn main() {"]
        body_lines = max(0, loc - 3)
        for i in range(body_lines):
            lines.append(f"    let x{i} = {i};")
        lines.append("    return 1;")
        lines.append("}")
        return "\n".join(lines)

    @pytest.mark.parametrize("name,loc,threshold", LOC_PROGRAMS)
    def test_compile_time_by_loc(self, name: str, loc: int, threshold: float) -> None:
        """Compile time scales reasonably with program size."""
        source = self._generate_loc_program(loc)
        repo_root = Path(__file__).resolve().parents[1]
        start = time.perf_counter()
        _compile_ail_source(source, repo_root)
        elapsed = time.perf_counter() - start
        assert (
            elapsed < threshold
        ), f"{name} compile took {elapsed:.3f}s (>{threshold}s)"


# =============================================================================
# LOC-based Memory Benchmarks
# =============================================================================


class TestMemoryByLOC:
    """Measure peak memory during compilation for programs of increasing size."""

    LOC_PROGRAMS: list[tuple[str, int, int]] = [
        ("mem_100_loc", 100, 200),
        ("mem_500_loc", 500, 300),
        ("mem_1000_loc", 1000, 400),
        ("mem_5000_loc", 5000, 500),
    ]

    def _generate_loc_program(self, loc: int) -> str:
        lines = ["fn main() {"]
        body_lines = max(0, loc - 3)
        for i in range(body_lines):
            lines.append(f"    let x{i} = {i};")
        lines.append("    return 1;")
        lines.append("}")
        return "\n".join(lines)

    @pytest.mark.parametrize("name,loc,threshold_mb", LOC_PROGRAMS)
    def test_compile_memory_by_loc(
        self, name: str, loc: int, threshold_mb: int
    ) -> None:
        """Peak memory during compilation stays within bounds."""
        source = self._generate_loc_program(loc)
        repo_root = Path(__file__).resolve().parents[1]
        tracemalloc.start()
        try:
            _compile_ail_source(source, repo_root)
            _current, peak = tracemalloc.get_traced_memory()
            peak_mb = peak / (1024 * 1024)
            assert (
                peak_mb < threshold_mb
            ), f"{name} peak memory {peak_mb:.1f}MB (>{threshold_mb}MB)"
        finally:
            tracemalloc.stop()


# =============================================================================
# Determinism by IR Hash
# =============================================================================


class TestDeterministicCompilation:
    """Verify that identical sources produce identical compiled output."""

    def _compile_and_hash(self, source: str) -> int:
        import hashlib
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            main_file = tmp_path / "main.ail"
            main_file.write_text(source)

            repo_root = Path(__file__).resolve().parents[1]
            session = CompilationSession()
            session._root = repo_root
            session._resolver = type(session._resolver)(repo_root)
            session.discover(main_file)

            reporter = DiagnosticReporter()
            session.analyze(reporter)
            assert reporter.error_count == 0

            bundle = session.build_ir()

            h = hashlib.sha256()
            for mod_name in bundle.module_irs:
                ir = bundle.module_irs[mod_name]
                h.update(str(ir).encode("utf-8"))
            return h.hexdigest()

    def test_deterministic_ir_produces_same_hash(self) -> None:
        """Same source compiled 3 times produces identical IR hash."""
        source = """
import string;
import math;
fn compute(a, b) {
    let s = string.uppercase("hello");
    let m = math.add(a, b);
    return m;
}
fn main() {
    let r = compute(3, 4);
    if (r == 7) {
        return 1;
    }
    return 0;
}
"""
        hashes: list[str] = []
        for _ in range(3):
            hashes.append(self._compile_and_hash(source))
        for h in hashes:
            assert h == hashes[0], f"Non-deterministic IR hash: {hashes}"

    def test_deterministic_ir_with_stdlib_imports(self) -> None:
        """Stdlib-importing program produces identical IR across 3 compiles."""
        source = """
import json;
import csv;
import list;
import map;
import file;
import path;
fn main() {
    let data = json.parse("{\\"a\\": 1}");
    let rows = csv.parse("x,y\\n1,2");
    let items = list.new();
    list.append(items, 1);
    return 1;
}
"""
        hashes: list[str] = []
        for _ in range(3):
            hashes.append(self._compile_and_hash(source))
        for h in hashes:
            assert h == hashes[0], f"Non-deterministic IR hash: {hashes}"

    def test_deterministic_large_program(self) -> None:
        """Large program (~200 LOC) produces identical IR across 3 compiles."""
        lines = ["import string;", "import math;", "", "fn a(x) { return x + 1; }"]
        for i in range(150):
            lines.append(f"fn f{i}(n) {{ return n + {i}; }}")
        lines.append("fn main() { return 1; }")
        source = "\n".join(lines)

        hashes: list[str] = []
        for _ in range(3):
            hashes.append(self._compile_and_hash(source))
        for h in hashes:
            assert (
                h == hashes[0]
            ), f"Non-deterministic IR hash for large program: {hashes}"

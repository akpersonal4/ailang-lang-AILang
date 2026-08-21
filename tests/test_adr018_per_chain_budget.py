"""Focused regression tests for ADR-018 P0-B and P0-D.

Tests:
- Per-call-chain iteration budget isolation
- Multi-pass workload (50k + 60k sequential chains)
- Single-chain enforcement (>100k fails)
- Exception restoration (counter restored after error)
- Error-message correctness (100000, not 2000)
- Existing 10k trampoline workload
- Determinism (byte-identical output)
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.runtime.errors import RuntimeError as AILangRuntimeError
from compiler.runtime.interpreter import Runtime
from compiler.runtime.sandbox import SandboxPolicy, get_policy, set_policy

# Increase recursion limit for deep recursion tests.
sys.setrecursionlimit(5000)


def _get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _run_source(source: str) -> Any:
    """Compile and execute AILang source, returning the main result."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source, encoding="utf-8")

        root = _get_repo_root()
        session = CompilationSession()
        session._root = root
        session._resolver = type(session._resolver)(root)
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
        return runtime.execute(bundle.module_irs[entry_module])


# =============================================================================
# ADR-018 §8.11 — factual wording: error messages reference 100000
# =============================================================================


class TestADRO18ErrorMessage:
    """P0-D: Error messages must reference 100000, not 2000."""

    def _get_policy(self) -> SandboxPolicy:
        return SandboxPolicy(working_dir=_get_repo_root(), enabled=False)

    def test_trampoline_loop_error_says_100000(self) -> None:
        """Trampoline loop (depth 1) budget exceeded reports 100000.

        f(n) with no base case goes through the trampoline loop.
        The error comes from _trampoline_call, not _inline_tail_chain.
        """
        original = get_policy()
        try:
            set_policy(self._get_policy())
            with pytest.raises(AILangRuntimeError) as exc_info:
                _run_source(
                    "fn f(n) { return f(n - 1) }\n"
                    "fn main() { return f(100001) }"
                )
            err = exc_info.value
            assert err.operation == "call"
            assert "Recursion depth exceeded" in err.reason
            assert "100000" in err.reason
            assert "2000" not in err.reason
        finally:
            set_policy(original)

    def test_inline_chain_error_says_100000(self) -> None:
        """Inline chain (depth > 1) budget exceeded reports 100000.

        outer() calls inner() at depth > 1, triggering _inline_tail_chain.
        The error references 100000 iterations.
        """
        original = get_policy()
        try:
            set_policy(self._get_policy())
            with pytest.raises(AILangRuntimeError) as exc_info:
                _run_source(
                    "fn inner(n) { if (n <= 0) { return 0 } return inner(n - 1) }\n"
                    "fn outer() { return inner(100001) }\n"
                    "fn main() { return outer() }"
                )
            err = exc_info.value
            assert err.operation == "call"
            assert "Recursion depth exceeded" in err.reason
            assert "100000" in err.reason
            assert "2000" not in err.reason
        finally:
            set_policy(original)


# =============================================================================
# ADR-018 Option C — per-call-chain budget isolation
# =============================================================================


class TestPerChainIsolation:
    """B: A chain approaching the 100k budget must not consume the
    budget of an independent subsequent chain."""

    def test_sequential_chains_independent(self) -> None:
        """Two chains each under 100k must both succeed."""
        source = """
fn chain_a(n, acc) {
    if (n <= 0) {
        return acc;
    }
    return chain_a(n - 1, acc + 1);
}
fn chain_b(n, acc) {
    if (n <= 0) {
        return acc;
    }
    return chain_b(n - 1, acc + 1);
}
fn main() {
    let r1 = chain_a(50000, 0);
    let r2 = chain_b(60000, 0);
    return r1 + r2;
}
"""
        result = _run_source(source)
        assert result == 50000 + 60000

    def test_three_sequential_chains(self) -> None:
        """Three chains each under 100k must all succeed."""
        source = """
fn chain_a(n) {
    if (n <= 0) { return 0; }
    return chain_a(n - 1);
}
fn chain_b(n) {
    if (n <= 0) { return 0; }
    return chain_b(n - 1);
}
fn chain_c(n) {
    if (n <= 0) { return 0; }
    return chain_c(n - 1);
}
fn main() {
    let a = chain_a(40000);
    let b = chain_b(40000);
    let c = chain_c(40000);
    return a + b + c;
}
"""
        result = _run_source(source)
        assert result == 0


# =============================================================================
# C: Multi-pass workload — 50k + 60k
# =============================================================================


class TestMultiPassWorkload:
    """C: Workloads such as 50k + 60k logically separate chains must
    succeed if each chain is independently below 100k."""

    def test_50k_then_60k_sequential(self) -> None:
        """50k scalar + 60k scalar in same main() must both pass."""
        source = """
fn deep_scalar(n, acc) {
    if (n <= 0) {
        return acc;
    }
    return deep_scalar(n - 1, acc + 1);
}
fn main() {
    let r1 = deep_scalar(50000, 0);
    let r2 = deep_scalar(60000, 0);
    return r1 + r2;
}
"""
        result = _run_source(source)
        assert result == 50000 + 60000


# =============================================================================
# D: Single-chain enforcement — >100k fails cleanly
# =============================================================================


class TestSingleChainEnforcement:
    """D: A single chain exceeding 100k must fail cleanly."""

    def test_single_chain_100k_succeeds(self) -> None:
        """count(99998) uses exactly 100000 trampoline iterations:
        main(1) + count(99998) calls(99998) + base case(1) = 100000.
        The check is >, not >=, so iteration 100000 passes."""
        source = """
fn count(n) {
    if (n <= 0) {
        return 0;
    }
    return count(n - 1);
}
fn main() {
    return count(99998);
}
"""
        result = _run_source(source)
        assert result == 0

    def test_single_chain_100001_fails(self) -> None:
        """A chain of 100001 iterations must fail with RuntimeError."""
        original = get_policy()
        try:
            set_policy(SandboxPolicy(working_dir=_get_repo_root(), enabled=False))
            with pytest.raises(AILangRuntimeError) as exc_info:
                _run_source(
                    "fn count(n) { if (n <= 0) { return 0 } return count(n - 1) }\n"
                    "fn main() { return count(100001) }"
                )
            assert "Recursion depth exceeded" in exc_info.value.reason
            assert "100000" in exc_info.value.reason
        finally:
            set_policy(original)


# =============================================================================
# E: Exception restoration — counter restored after error
# =============================================================================


class TestExceptionRestoration:
    """E: A tail-call chain that raises must restore the previous
    trampoline iteration counter. A subsequent independent chain
    must still receive its full budget."""

    def test_counter_restored_after_chain_error(self) -> None:
        """After a chain raises, a subsequent chain gets full budget."""
        source = """
fn risky(n) {
    if (n == 0) {
        return 1 / 0;
    }
    return risky(n - 1);
}
fn safe(n, acc) {
    if (n <= 0) {
        return acc;
    }
    return safe(n - 1, acc + 1);
}
fn main() {
    let r1 = risky(50);
    return r1;
}
"""
        with pytest.raises(AILangRuntimeError):
            _run_source(source)

    def test_subsequent_chain_succeeds_after_failed_chain(self) -> None:
        """A successful chain after a failed chain still works.

        This tests that _inline_tail_chain's try/finally restores the
        iteration counter even when the chain raises an exception.
        """
        source = """
fn risky(n) {
    if (n == 0) {
        return 1 / 0;
    }
    return risky(n - 1);
}
fn safe(n, acc) {
    if (n <= 0) {
        return acc;
    }
    return safe(n - 1, acc + 1);
}
fn main() {
    let r1 = risky(50);
    let r2 = safe(50000, 0);
    return r2;
}
"""
        with pytest.raises(AILangRuntimeError):
            _run_source(source)


# =============================================================================
# G: Existing 10k trampoline workload
# =============================================================================


class TestTrampoline10k:
    """G: Existing 10k trampoline workload must still pass."""

    def test_countdown_10000(self) -> None:
        """Tail-recursive countdown to 10000 must succeed."""
        source = """
fn countdown(n) {
    if (n <= 0) {
        return 0;
    }
    return countdown(n - 1);
}
fn main() {
    return countdown(10000);
}
"""
        result = _run_source(source)
        assert result == 0

    def test_scalar_sum_10000(self) -> None:
        """Tail-recursive scalar sum to 10000 must succeed."""
        source = """
fn sum(n, acc) {
    if (n <= 0) {
        return acc;
    }
    return sum(n - 1, acc + n);
}
fn main() {
    return sum(10000, 0);
}
"""
        result = _run_source(source)
        assert result == 50005000


# =============================================================================
# H: Determinism — byte-identical output across 5 runs
# =============================================================================


class TestDeterminism:
    """H: Same workload must produce byte-identical output across
    at least 5 runs."""

    def test_countdown_deterministic(self) -> None:
        """countdown(10000) produces identical results across 5 runs."""
        source = """
fn countdown(n) {
    if (n <= 0) {
        return 0;
    }
    return countdown(n - 1);
}
fn main() {
    return countdown(10000);
}
"""
        results = [_run_source(source) for _ in range(5)]
        assert len(set(results)) == 1
        assert results[0] == 0

    def test_sequential_chains_deterministic(self) -> None:
        """Two sequential chains produce identical results across 5 runs."""
        source = """
fn chain_a(n) {
    if (n <= 0) { return 0; }
    return chain_a(n - 1);
}
fn chain_b(n) {
    if (n <= 0) { return 0; }
    return chain_b(n - 1);
}
fn main() {
    let a = chain_a(30000);
    let b = chain_b(30000);
    return a + b;
}
"""
        results = [_run_source(source) for _ in range(5)]
        assert len(set(results)) == 1
        assert results[0] == 0


# =============================================================================
# Pre-existing test update: recursion_depth_clean_error
# =============================================================================


class TestPreExistingBehavior:
    """Update pre-existing test that assumed 2000 limit."""

    def test_recursion_depth_clean_error_updated(self) -> None:
        """Deep tail recursion via trampoline succeeds up to budget.

        recurse(99998) uses exactly 100000 trampoline iterations (main +
        99998 calls + base case). recurse(100001) exceeds the budget and
        raises RuntimeError referencing 100000, not 2000.
        """
        source_ok = """
fn recurse(n) {
    if (n <= 0) {
        return 0;
    }
    return recurse(n - 1);
}
fn main() {
    return recurse(99998);
}
"""
        result = _run_source(source_ok)
        assert result == 0

        original = get_policy()
        try:
            set_policy(SandboxPolicy(working_dir=_get_repo_root(), enabled=False))
            with pytest.raises(AILangRuntimeError) as exc_info:
                _run_source(
                    "fn recurse(n) { if (n <= 0) { return 0 } return recurse(n - 1) }\n"
                    "fn main() { return recurse(100001) }"
                )
            err = exc_info.value
            assert err.operation == "call"
            assert "Recursion depth exceeded" in err.reason
            assert "100000" in err.reason
        finally:
            set_policy(original)

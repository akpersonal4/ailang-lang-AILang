"""Tests for the experimental for-in loop primitive (--experimental-loops).

These tests verify parsing, semantic analysis, IR lowering, and runtime
execution of for-in loops, which are lowered into recursive function calls
during IR construction. All tests require ``--experimental-loops``.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.runtime.interpreter import Runtime


def _run_with_loops(source: str) -> int:
    """Compile and run an AILang source with --experimental-loops enabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

        repo_root = Path(__file__).resolve().parents[1]
        session = CompilationSession(experimental_loops=True)
        session._root = repo_root
        session._resolver = type(session._resolver)(repo_root)
        session.discover(main_file)

        reporter = DiagnosticReporter()
        session.analyze(reporter)
        assert (
            reporter.error_count == 0
        ), f"Compile errors: {[d.message for d in reporter.diagnostics]}"

        bundle = session.build_ir()
        runtime = Runtime(bundle)
        for module_name in session._graph.topological_sort():
            runtime._initialize_module(module_name)

        entry_module = next(name for name in bundle.module_irs if name.endswith("main"))
        return int(runtime.execute(bundle.module_irs[entry_module]))


# =============================================================================
# Basic iteration
# =============================================================================


def test_for_sum_list() -> None:
    """Sum all elements of a list using for-in."""
    result = _run_with_loops("""
import list;
fn main() {
    let items = list.new();
    list.append(items, 10);
    list.append(items, 20);
    list.append(items, 30);
    let total = 0;
    for item in items {
        total = total + item;
    }
    return total;
}
""")
    assert result == 60


def test_for_count_items() -> None:
    """Count elements by incrementing a counter inside the loop."""
    result = _run_with_loops("""
import list;
fn main() {
    let items = list.new();
    list.append(items, "a");
    list.append(items, "b");
    list.append(items, "c");
    let count = 0;
    for x in items {
        count = count + 1;
    }
    return count;
}
""")
    assert result == 3


def test_for_max_element() -> None:
    """Find the maximum element in a list."""
    result = _run_with_loops("""
import list;
fn main() {
    let items = list.new();
    list.append(items, 3);
    list.append(items, 7);
    list.append(items, 2);
    list.append(items, 9);
    list.append(items, 1);
    let mx = 0;
    for val in items {
        if (val > mx) {
            mx = val;
        }
    }
    return mx;
}
""")
    assert result == 9


# =============================================================================
# Edge cases
# =============================================================================


def test_for_empty_list() -> None:
    """Loop over an empty list should not execute body."""
    result = _run_with_loops("""
import list;
fn main() {
    let items = list.new();
    let total = 0;
    for item in items {
        total = total + 1;
    }
    return total;
}
""")
    assert result == 0


def test_for_single_element() -> None:
    """Loop over a list with one element."""
    result = _run_with_loops("""
import list;
fn main() {
    let items = list.new();
    list.append(items, 42);
    let total = 0;
    for item in items {
        total = total + item;
    }
    return total;
}
""")
    assert result == 42


# =============================================================================
# Nested loops
# =============================================================================


def test_for_nested() -> None:
    """Nested for-in loops (2D list traversal)."""
    result = _run_with_loops("""
import list;
fn main() {
    let outer = list.new();
    let inner1 = list.new();
    list.append(inner1, 1);
    list.append(inner1, 2);
    list.append(outer, inner1);
    let inner2 = list.new();
    list.append(inner2, 3);
    list.append(inner2, 4);
    list.append(outer, inner2);
    let total = 0;
    for row in outer {
        for cell in row {
            total = total + cell;
        }
    }
    return total;
}
""")
    assert result == 10


# =============================================================================
# For loop inside a function called from main
# =============================================================================


def test_for_in_helper_function() -> None:
    """For loop inside a separate helper function."""
    result = _run_with_loops("""
import list;
fn sum_list(items) {
    let total = 0;
    for item in items {
        total = total + item;
    }
    return total;
}
fn main() {
    let items = list.new();
    list.append(items, 5);
    list.append(items, 10);
    list.append(items, 15);
    return sum_list(items);
}
""")
    assert result == 30


# =============================================================================
# Flag guard — without --experimental-loops
# =============================================================================


def test_for_rejected_without_flag() -> None:
    """Using 'for' without --experimental-loops should produce an error."""
    source = """
import list;
fn main() {
    let items = list.new();
    for item in items {
        print(item);
    }
    return 0;
}
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

        repo_root = Path(__file__).resolve().parents[1]
        session = CompilationSession(experimental_loops=False)  # flag OFF
        session._root = repo_root
        session._resolver = type(session._resolver)(repo_root)
        reporter = DiagnosticReporter()
        session.discover(main_file, reporter)

        session.analyze(reporter)
        assert (
            reporter.error_count > 0
        ), "Expected errors when --experimental-loops is off"


def test_for_print_elements() -> None:
    """For loop calling print inside body."""
    result = _run_with_loops("""
import list;
fn main() {
    let items = list.new();
    list.append(items, 100);
    list.append(items, 200);
    let last = 0;
    for item in items {
        last = item;
    }
    return last;
}
""")
    assert result == 200


# =============================================================================
# Capture semantics
# =============================================================================


def test_for_read_only_capture() -> None:
    """Read-only enclosing variable is threaded through."""
    result = _run_with_loops("""
import list;
fn main() {
    let items = list.new();
    list.append(items, 1);
    list.append(items, 2);
    list.append(items, 3);
    let offset = 10;
    let total = 0;
    for item in items {
        total = total + item + offset;
    }
    return total;
}
""")
    assert result == (1 + 2 + 3) + 3 * 10


def test_for_read_only_multiple() -> None:
    """Multiple read-only enclosing variables."""
    result = _run_with_loops("""
import list;
fn main() {
    let items = list.new();
    list.append(items, 1);
    list.append(items, 2);
    let a = 1;
    let b = 2;
    let total = 0;
    for item in items {
        total = total + item + a + b;
    }
    return total;
}
""")
    assert result == (1 + 1 + 2) + (2 + 1 + 2)


def test_for_mixed_read_write() -> None:
    """Read-only and write captures together."""
    result = _run_with_loops("""
import list;
fn main() {
    let items = list.new();
    list.append(items, 1);
    list.append(items, 2);
    list.append(items, 3);
    let factor = 2;
    let total = 0;
    for item in items {
        total = total + item * factor;
    }
    return total;
}
""")
    assert result == (1 * 2) + (2 * 2) + (3 * 2)


def test_for_capture_in_if_body() -> None:
    """Enclosing variable written inside an if in the loop body."""
    result = _run_with_loops("""
import list;
fn main() {
    let items = list.new();
    list.append(items, 1);
    list.append(items, 2);
    list.append(items, 3);
    list.append(items, 4);
    list.append(items, 5);
    let total = 0;
    for item in items {
        if (item > 3) {
            total = total + item;
        } else {
            total = total;
        }
    }
    return total;
}
""")
    assert result == 4 + 5


def test_for_capture_no_accumulator() -> None:
    """Read-only capture without a write accumulator."""
    result = _run_with_loops("""
import list;
fn main() {
    let items = list.new();
    list.append(items, "a");
    list.append(items, "b");
    let seen = 0;
    for item in items {
        seen = seen + 1;
    }
    return seen;
}
""")
    assert result == 2


def test_for_capture_flag_guard() -> None:
    """Loop body uses a flag variable via capture."""
    result = _run_with_loops("""
import list;
fn main() {
    let items = list.new();
    list.append(items, 1);
    list.append(items, 2);
    list.append(items, 3);
    let found = 0;
    for item in items {
        if (item == 2) {
            found = 1;
        }
    }
    return found;
}
""")
    assert result == 1


def test_for_multiple_writes_rejected() -> None:
    """Two accumulator variables raise ValueError."""
    source = """
import list;
fn main() {
    let items = list.new();
    list.append(items, 1);
    list.append(items, 2);
    let total = 0;
    let count = 0;
    for item in items {
        total = total + item;
        count = count + 1;
    }
    return total;
}
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

        repo_root = Path(__file__).resolve().parents[1]
        session = CompilationSession(experimental_loops=True)
        session._root = repo_root
        session._resolver = type(session._resolver)(repo_root)
        session.discover(main_file)

        reporter = DiagnosticReporter()
        session.analyze(reporter)
        assert reporter.error_count == 0

        with pytest.raises(ValueError, match="Only one accumulator"):
            session.build_ir()

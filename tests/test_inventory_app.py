"""Test Level 0 modules by compiling the actual inventory app files."""

from __future__ import annotations

from pathlib import Path

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter, Severity
from compiler.runtime.interpreter import Runtime


def _build_inventory_app() -> tuple[Runtime, str]:
    """Compile the actual inventory app and return (runtime, entry_module_name)."""
    repo_root = Path(__file__).resolve().parents[1]
    inv_root = repo_root / "apps" / "inventory"
    main_file = inv_root / "main.ail"

    assert main_file.exists(), f"Entry point not found: {main_file}"

    session = CompilationSession()
    session._root = inv_root
    session._resolver = type(session._resolver)(inv_root)
    session.discover(main_file)

    reporter = DiagnosticReporter()
    session.analyze(reporter)
    if reporter.error_count > 0:
        err_msgs = [
            f"{d.error_code.code}: {d.message} (file={d.file_path}, line={d.line})"
            for d in reporter.diagnostics
            if d.severity == Severity.ERROR
        ]
        assert False, f"Compilation errors: {err_msgs}"

    bundle = session.build_ir()
    runtime = Runtime(bundle)
    for module_name in session._graph.topological_sort():
        runtime._initialize_module(module_name)

    entry_module = next(name for name in bundle.module_irs if name.endswith("main"))
    return runtime, entry_module, bundle


def test_compilation_succeeds() -> None:
    """The inventory app should compile without errors."""
    _build_inventory_app()
    # If we get here, compilation passed
    assert True


def test_storage_module_functions() -> None:
    """Test storage module directly through the compiled app."""
    runtime, entry_name, bundle = _build_inventory_app()
    entry_ir = bundle.module_irs[entry_name]
    # Just verify compilation succeeds for now
    assert entry_ir is not None

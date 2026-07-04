#!/usr/bin/env python
"""AILang CLI entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.runtime.interpreter import Runtime


def run(file_path: str) -> int:
    """Compile and run an AILang program.

    Args:
        file_path: Path to the .ail source file

    Returns:
        Exit code (0 for success, 1 for error)
    """
    source_path = Path(file_path).resolve()

    if not source_path.exists():
        print(f"Error: File not found: {source_path}", file=sys.stderr)
        return 1

    root_dir = source_path.parent

    session = CompilationSession()
    session._root = root_dir
    session._resolver = type(session._resolver)(root_dir)

    reporter = DiagnosticReporter()
    session.discover(source_path)
    session.analyze(reporter)

    if reporter.error_count > 0:
        for diagnostic in reporter.diagnostics:
            print(f"Error: {diagnostic.message}", file=sys.stderr)
        return 1

    bundle = session.build_ir()
    runtime = Runtime(bundle)

    for module_name in session._graph.topological_sort():
        runtime._initialize_module(module_name)

    try:
        # Find the main module (entry point)
        main_module = None
        for module_name in session._graph.topological_sort():
            if module_name in bundle.module_irs:
                main_module = module_name
                break

        if main_module is None:
            raise KeyError("No module found")

        program_ir = bundle.module_irs[main_module]
        runtime.execute(program_ir)
        return 0
    except Exception as e:
        print(f"Runtime error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="ail", description="AILang compiler and runtime"
    )
    parser.add_argument("file", help="Path to the .ail source file")
    args = parser.parse_args()
    return run(args.file)


if __name__ == "__main__":
    sys.exit(main())

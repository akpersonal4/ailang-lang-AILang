# AILang MCP Server - Compiler Adapter
# Uses existing compiler pipeline for compilation

"""Compiler adapter for MCP server - compiles AILang source and returns diagnostics."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any


def compile_source(source: str) -> dict[str, Any]:
    """Compile AILang source code and return diagnostics.

    Args:
        source: AILang source code to compile

    Returns:
        Dictionary with success status and diagnostics
    """
    try:
        from compiler.cli.main import _find_stdlib
        from compiler.compilation import CompilationSession
        from compiler.diagnostics import DiagnosticReporter

        # Create a temporary file with the source
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ail", delete=False, encoding="utf-8"
        ) as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            # Find stdlib and root
            stdlib_dir = _find_stdlib()
            root_dir = stdlib_dir.parent

            # Create a compilation session
            session = CompilationSession()
            session._root = root_dir
            session._resolver = type(session._resolver)(root_dir)

            # Create a reporter
            reporter = DiagnosticReporter()

            # Discover and compile
            session.discover(temp_path, reporter)

            # Analyze
            session.analyze(reporter)

            # Type check
            try:
                session.type_check(reporter)
            except Exception as e:
                # Internal compiler error
                from compiler.diagnostics import Diagnostic, ErrorCode, Severity

                diag = Diagnostic(
                    Severity.ERROR,
                    ErrorCode("CMP001", "Internal compiler error"),
                    str(e),
                    file_path=str(temp_path),
                )
                reporter.report(diag)

            # Check for diagnostics
            diagnostics = []
            if reporter:
                for diag in reporter.diagnostics:
                    diagnostics.append(
                        {
                            "code": diag.code,
                            "message": diag.message,
                            "line": getattr(diag, "line", None),
                            "column": getattr(diag, "column", None),
                            "severity": getattr(diag, "severity", "error"),
                        }
                    )

            success = len(diagnostics) == 0

            return {
                "success": success,
                "diagnostics": diagnostics,
            }

        finally:
            # Clean up temporary file
            temp_path.unlink(missing_ok=True)

    except Exception as e:
        return {
            "success": False,
            "diagnostics": [
                {
                    "code": "CMP001",
                    "message": f"Internal compiler error: {str(e)}",
                    "line": None,
                    "column": None,
                    "severity": "error",
                }
            ],
        }

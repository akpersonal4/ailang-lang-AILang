#!/usr/bin/env python
"""AILang CLI entry point — the `ail` command.

Usage:
    ail run <file>       Compile and run an AILang program
    ail build <file>     Compile and check for errors (no execution)
    ail check <file>     Check for forward references and ordering violations
    ail fmt <file>       Format AILang source files
    ail test             Run test_*.ail files
    ail docs <name>      Retrieve documentation (AGENTS, LANGUAGE_SPEC, STDLIB_REFERENCE)
    ail explain <CODE>   Explain a compiler error code in detail
    ail context [--json] Generate AI-friendly project context
    ail mcp              Start MCP server for AI tool integration
    ail version          Print version information
    ail help             Print this help message
    ail <file>           Shorthand for `ail run <file>`
"""

from __future__ import annotations

import difflib
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from compiler import __version__
from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticFormatter, DiagnosticReporter
from compiler.runtime import builtins as runtime_builtins
from compiler.runtime.interpreter import Runtime

PROG = "ail"

# =============================================================================
# Development mode controls — M78 Design Improvement
# =============================================================================

_DEV_MODE = False  # Set to True via --dev flag or AILANG_DEV_ROOT env var
_DEV_ROOT_OVERRIDE = os.environ.get("AILANG_DEV_ROOT")  # Explicit dev root path


# =============================================================================
# First-run experience
# =============================================================================


def _get_config_dir() -> Path:
    """Get the AILang config directory (~/.ail)."""
    config_dir = Path.home() / ".ail"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def _get_state_file() -> Path:
    """Get the state file path (~/.ail/state.json)."""
    return _get_config_dir() / "state.json"


def _load_state() -> dict:
    """Load the state file, returning empty dict if not found."""
    import json

    state_file = _get_state_file()
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_state(state: dict) -> None:
    """Save the state file."""
    import json

    state_file = _get_state_file()
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _is_first_run() -> bool:
    """Check if this is the first run of AILang."""
    state = _load_state()
    return not state.get("onboarded", False)


def _mark_onboarded() -> None:
    """Mark the first-run experience as completed."""
    state = _load_state()
    state["onboarded"] = True
    state["version"] = __version__
    _save_state(state)


def _show_welcome() -> None:
    """Display the first-run welcome message."""
    print("""
Welcome to AILang.

Recommended startup sequence:

  1. ail doctor          Check your environment
  2. ail docs AGENTS     Read the AI agent instructions
  3. ail context --json  Get machine-readable language context
  4. ail fmt             Format your code
  5. ail check           Validate before building
  6. ail build           Compile and check for errors
  7. ail run             Compile and execute

For more help: ail --help
""")
    _mark_onboarded()


def _find_stdlib() -> Path:
    """Locate the stdlib directory.

    Order (M78 Design Improvement):
    1. Next to the compiler package (highest priority: installed packages).
    2. Next to the compiler package parent (editable installs).
    3. Walk up from CWD ONLY if dev mode is enabled (AILANG_DEV_ROOT or --dev).
    4. Fallback to a bundled path inside site-packages.
    5. Last resort: stdlib next to the compiler package root.

    Production mode NEVER walks upward, preventing accidental repository coupling.
    """
    # Path of the current file = compiler/cli/main.py
    this_file = Path(__file__).resolve()
    pkg_dir = this_file.parent.parent.parent  # site-packages/ or repo root

    # 1. Check next to the compiler package (installed wheel: site-packages/stdlib/)
    #    This has HIGHEST priority - never bypassed
    candidate = pkg_dir / "stdlib"
    if candidate.is_dir() and any(candidate.iterdir()):
        return candidate

    # 2. Check next to the compiler package parent (dev tree: repo-root/)
    parent_candidate = pkg_dir.parent / "stdlib"
    if parent_candidate.is_dir() and any(parent_candidate.iterdir()):
        return parent_candidate

    # 3. Walk up from CWD - ONLY in dev mode
    # Production installations must NEVER walk upward
    dev_mode = _DEV_MODE or (_DEV_ROOT_OVERRIDE is not None)
    if dev_mode:
        # If AILANG_DEV_ROOT is set, use it directly
        if _DEV_ROOT_OVERRIDE:
            dev_root = Path(_DEV_ROOT_OVERRIDE).resolve()
            dev_stdlib = dev_root / "stdlib"
            if dev_stdlib.is_dir():
                return dev_stdlib
        # Otherwise walk upward from CWD
        for start in [Path.cwd(), pkg_dir]:
            current = start
            while True:
                if (current / "stdlib").is_dir() and (
                    current / "pyproject.toml"
                ).is_file():
                    return current / "stdlib"
                if current == current.parent:
                    break
                current = current.parent

    # 4. Fallback: look inside site-packages for a bundled stdlib copy
    import site

    for site_dir in site.getsitepackages():
        bundled = Path(site_dir) / "ailang" / "stdlib"
        if bundled.is_dir():
            return bundled
        # also try flat site-packages/stdlib/
        flat = Path(site_dir) / "stdlib"
        if flat.is_dir():
            return flat

    # 5. Last resort: what we have
    return pkg_dir / "stdlib"


def _get_version() -> str:
    return f"AILang v{__version__}"


# =============================================================================
# Command implementations
# =============================================================================


def _compile(
    source_path: Path,
    json_mode: bool = False,
    experimental_loops: bool = False,
    root_override: str | None = None,
    quiet: bool = False,
) -> tuple[CompilationSession | None, DiagnosticReporter]:
    """Compile a source file and return the session and reporter.

    Args:
        root_override: If set, use this directory as the project root for
            module resolution instead of source_path.parent. This is needed
            when test files live in a subdirectory (tests/) and import
            modules from the parent app directory.
        quiet: If True, suppress diagnostic output to stderr.

    Returns:
        tuple of (session, reporter) where session is None on error.
    """
    if not source_path.exists():
        print(f"Error: File not found: {source_path}", file=sys.stderr)
        return None, DiagnosticReporter()

    stdlib_dir = _find_stdlib()
    root_dir = stdlib_dir.parent

    session = CompilationSession(experimental_loops=experimental_loops)
    if root_override:
        resolve_root = Path(root_override).resolve()
    else:
        resolve_root = source_path.parent.resolve()
    session._root = resolve_root
    session._resolver = type(session._resolver)(resolve_root)

    reporter = DiagnosticReporter()
    session.discover(source_path, reporter)

    session.analyze(reporter)
    # -------------------------------------------------
    # Run type checking – part of the required compilation pipeline
    # -------------------------------------------------
    try:
        session.type_check(reporter)
    except Exception as e:
        # Internal compiler error – emit CMP001 diagnostic
        from compiler.diagnostics import Diagnostic, ErrorCode, Severity

        diag = Diagnostic(
            Severity.ERROR,
            ErrorCode("CMP001", "Internal compiler error"),
            str(e),
            file_path=str(source_path),
        )
        reporter.report(diag)
        if not json_mode:
            formatter = DiagnosticFormatter()
            print(formatter.format(diag), file=sys.stderr)
        return None, reporter
    # -------------------------------------------------

    if reporter.error_count > 0:
        if not json_mode and not quiet:
            formatter = DiagnosticFormatter()
            for diagnostic in reporter.diagnostics:
                print(formatter.format(diagnostic), file=sys.stderr)
            # Print summary with next steps
            summary = DiagnosticFormatter.format_summary(reporter, str(source_path))
            if summary:
                print(f"\n{summary}", file=sys.stderr)
        return None, reporter

    return session, reporter


def cmd_run(args: list[str]) -> int:
    """Compile and run an AILang program.

    Automatically runs ail check before compilation to detect
    forward references, missing imports, and ordering violations.
    If check fails, execution stops with actionable fixes.
    """
    experimental_loops = False
    no_check = False
    positional: list[str] = []

    remaining = list(args)
    while remaining:
        arg = remaining.pop(0)
        if arg == "--experimental-loops":
            experimental_loops = True
        elif arg == "--no-check":
            no_check = True
        elif arg.startswith("-"):
            print(
                f"Usage: {PROG} run [--experimental-loops] [--no-check] <file>",
                file=sys.stderr,
            )
            return 1
        else:
            positional.append(arg)

    if not positional:
        print("Error: missing file argument", file=sys.stderr)
        print(
            f"Usage: {PROG} run [--experimental-loops] [--no-check] <file>",
            file=sys.stderr,
        )
        return 1

    source_path = Path(positional[0]).resolve()

    # Auto-check: detect forward references and ordering violations before compilation
    if not no_check:
        check_violations = _check_file_forward_references(source_path)
        if check_violations:
            formatter = DiagnosticFormatter()
            for v in check_violations:
                print()
                if v["type"] == "forward_reference":
                    print("FORWARD_REF:")
                elif v["type"] == "missing_import":
                    print("MISSING_IMPORT:")
                print(f"{v['file']}:{v['line']}")
                print()
                print(f"  {v['caller']}()")
                print(f"  calls {v['callee']}()")
                print()
                print("  Suggestion:")
                if v["type"] == "forward_reference":
                    print(f"    Move {v['callee']}() definition above {v['caller']}()")
                elif v["type"] == "missing_import":
                    print(f"    Add: import {v['module']};")
                print()
            print(f"Check failed: {len(check_violations)} violation(s) found.")
            print(
                "Fix these issues before running. Use --no-check to skip.",
                file=sys.stderr,
            )
            return 1

    # Strip CLI plumbing so env_args() returns only the user's args.
    # args[0] is the source file; everything after is user-provided.
    runtime_builtins._program_argv = positional[1:]

    session, _ = _compile(source_path, experimental_loops=experimental_loops)
    if session is None:
        return 1

    try:
        bundle = session.build_ir()
    except Exception as e:
        # Internal compiler error during IR generation
        from compiler.diagnostics import Diagnostic, ErrorCode, Severity

        diag = Diagnostic(
            Severity.ERROR,
            ErrorCode("CMP001", "Internal compiler error"),
            str(e),
            file_path=str(source_path),
        )
        formatter = DiagnosticFormatter()
        print(formatter.format(diag), file=sys.stderr)
        return 1
    runtime = Runtime(bundle)

    for module_name in session._graph.topological_sort():
        runtime._initialize_module(module_name)

    try:
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


def _format_errors_json(filepath: str, reporter: DiagnosticReporter) -> str:
    """Format diagnostics as JSON for machine consumption."""
    import json

    errors = [
        {
            "file": d.file_path or filepath,
            "line": d.line,
            "column": d.column,
            "code": d.error_code.code,
            "message": d.message,
            "severity": d.severity.name.lower(),
            "suggestion": d.suggestion,
        }
        for d in reporter.diagnostics
    ]
    return json.dumps({"passed": False, "errors": errors}, indent=2)


def cmd_build(args: list[str]) -> int:
    """Compile an AILang program and check for errors (no execution)."""
    json_mode = False
    experimental_loops = False
    paths: list[str] = []

    remaining = list(args)
    while remaining:
        arg = remaining.pop(0)
        if arg == "--json":
            json_mode = True
        elif arg == "--experimental-loops":
            experimental_loops = True
        elif arg.startswith("-"):
            print(f"Unknown option: {arg}", file=sys.stderr)
            print(
                f"Usage: {PROG} build [--json] [--experimental-loops] <file>",
                file=sys.stderr,
            )
            return 1
        else:
            paths.append(arg)

    if not paths:
        print("Error: missing file argument", file=sys.stderr)
        print(
            f"Usage: {PROG} build [--json] [--experimental-loops] <file>",
            file=sys.stderr,
        )
        return 1

    source_path = Path(paths[0]).resolve()
    session, reporter = _compile(source_path, json_mode, experimental_loops)

    if session is None:
        if json_mode:
            print(_format_errors_json(str(source_path), reporter))
        return 1

    if json_mode:
        # Build was successful, no errors
        import json

        result = {"passed": True, "errors": []}
        print(json.dumps(result))
    else:
        print(f"Build successful: {source_path}")
    return 0


def cmd_check(args: list[str]) -> int:
    """Check AILang source for semantic errors, type errors, forward references, and ordering violations.

    Runs the full compilation pipeline (discover → analyze → type_check)
    so that ail check and ail build report identical diagnostics.

    Usage:
        ail check <file>         Check a single file
        ail check <dir>          Check all .ail files in directory
        ail check --recursive .  Check all .ail files recursively

    Reports all violations in a single run with exact fix suggestions.
    """
    json_mode = False
    recursive = False
    paths: list[str] = []

    remaining = list(args)
    while remaining:
        arg = remaining.pop(0)
        if arg == "--json":
            json_mode = True
        elif arg == "--recursive":
            recursive = True
        elif arg.startswith("-"):
            print(f"Unknown option: {arg}", file=sys.stderr)
            print(
                f"Usage: {PROG} check [--json] [--recursive] <file_or_dir>",
                file=sys.stderr,
            )
            return 1
        else:
            paths.append(arg)

    if not paths:
        print("Error: missing file argument", file=sys.stderr)
        print(
            f"Usage: {PROG} check [--json] [--recursive] <file_or_dir>", file=sys.stderr
        )
        return 1

    # Collect files to check
    files_to_check: list[Path] = []
    for p in paths:
        path = Path(p).resolve()
        if not path.exists():
            print(f"Error: Path not found: {path}", file=sys.stderr)
            return 1
        if path.is_dir():
            if recursive:
                for found in sorted(path.rglob("*.ail")):
                    parts = found.parts
                    if any(skip in parts for skip in _FMT_SKIP_DIRS):
                        continue
                    files_to_check.append(found)
            else:
                for found in sorted(path.glob("*.ail")):
                    files_to_check.append(found)
        else:
            files_to_check.append(path)

    if not files_to_check:
        print("No .ail files found to check.", file=sys.stderr)
        return 1

    # Run full compilation pipeline on each file (discover → analyze → type_check)
    total_errors = 0
    all_reporters: list[tuple[Path, DiagnosticReporter]] = []

    for file_path in files_to_check:
        session, reporter = _compile(file_path, quiet=True)
        all_reporters.append((file_path, reporter))
        total_errors += reporter.error_count

    # Output results
    if json_mode:
        import json

        all_diags = []
        for file_path, reporter in all_reporters:
            for d in reporter.diagnostics:
                all_diags.append(
                    {
                        "file": d.file_path or str(file_path),
                        "line": d.line,
                        "column": d.column,
                        "code": d.error_code.code,
                        "message": d.message,
                        "severity": d.severity.name.lower(),
                        "suggestion": d.suggestion,
                    }
                )
        result = {
            "passed": total_errors == 0,
            "errors": all_diags,
            "total_errors": total_errors,
        }
        print(json.dumps(result, indent=2))
    else:
        if total_errors == 0:
            print(
                f"Check passed: {len(files_to_check)} file(s) checked, no errors found."
            )
        else:
            formatter = DiagnosticFormatter()
            for file_path, reporter in all_reporters:
                for diag in reporter.diagnostics:
                    print(formatter.format(diag), file=sys.stderr)
            print(
                f"\nTotal: {total_errors} error(s) in {len(files_to_check)} file(s)",
                file=sys.stderr,
            )

    return 1 if total_errors > 0 else 0


def _check_file_forward_references(file_path: Path) -> list[dict]:
    """Check a single file for forward references and missing imports.

    Returns a list of violation dictionaries with type, file, line, caller, callee, module.
    """
    violations: list[dict] = []

    if not file_path.exists():
        return violations

    try:
        source_text = file_path.read_text(encoding="utf-8")
    except Exception:
        return violations

    # Parse the file to get function definitions and calls
    try:
        from compiler.ast.builder import ASTBuilder
        from compiler.ast.nodes import (
            BinaryExpressionNode,
            BlockNode,
            CallExpressionNode,
            ExpressionStatementNode,
            ForStatementNode,
            FunctionDeclarationNode,
            IdentifierNode,
            IfStatementNode,
            ImportDeclarationNode,
            MemberAccessNode,
            ProgramNode,
            ReturnStatementNode,
            UnaryExpressionNode,
            VariableDeclarationNode,
        )
        from compiler.lexer import Lexer
        from compiler.parser import Parser

        lexer = Lexer(source_path=str(file_path))
        tokens = lexer.tokenize(source_text)
        parser = Parser(tokens, source_path=str(file_path))
        cst = parser.parse_program()
        ast = ASTBuilder().build(cst)

        if not isinstance(ast, ProgramNode):
            return violations

        # Helper to convert span to line number
        source_lines = source_text.split("\n")

        def span_to_line(span: int | None) -> int:
            if span is None:
                return 0
            offset = span
            for lineno, src_line in enumerate(source_lines, 1):
                if offset <= len(src_line):
                    return lineno
                offset -= len(src_line) + 1  # +1 for newline char
            return len(source_lines)

        # Collect function definitions with their line numbers
        function_defs: dict[str, int] = {}  # name -> line number
        function_def_order: list[str] = []  # Order of definitions

        # Collect imports
        imports: set[str] = set()  # imported module names

        # Collect calls with their line numbers
        calls: list[tuple[str, str, int]] = []  # (caller_context, callee, line)

        def _collect_declarations(node, context: str = "global"):
            """Collect function declarations and track their order."""
            if isinstance(node, FunctionDeclarationNode):
                func_name = node.name.name
                function_defs[func_name] = span_to_line(node.start_span)
                function_def_order.append(func_name)
                # Recurse into function body with this function as context
                _collect_declarations(node.body, func_name)
            elif isinstance(node, ProgramNode):
                for child in node.children:
                    _collect_declarations(child, context)
            elif isinstance(node, ImportDeclarationNode):
                module_path = ".".join(node.module_path)
                imports.add(module_path)
                # Also add the root module name
                imports.add(node.module_path[0])
            elif hasattr(node, "body"):
                # Recurse into other nodes with bodies (if, for, etc.)
                _collect_declarations(node.body, context)

        def _collect_calls(node, context: str = "global"):
            """Collect function calls."""
            if isinstance(node, CallExpressionNode):
                callee = node.callee
                if isinstance(callee, IdentifierNode):
                    calls.append((context, callee.name, span_to_line(node.start_span)))
                elif isinstance(callee, MemberAccessNode):
                    if isinstance(callee.receiver, IdentifierNode):
                        module_name = callee.receiver.name
                        func_name = callee.member.name
                        calls.append(
                            (
                                context,
                                f"{module_name}.{func_name}",
                                span_to_line(node.start_span),
                            )
                        )
                # Recurse into arguments
                for arg in node.arguments:
                    _collect_calls(arg, context)
            elif isinstance(node, ProgramNode):
                for child in node.children:
                    _collect_calls(child, context)
            elif isinstance(node, FunctionDeclarationNode):
                _collect_calls(node.body, node.name.name)
            elif isinstance(node, ImportDeclarationNode):
                pass  # Skip imports
            elif isinstance(node, VariableDeclarationNode):
                _collect_calls(node.initializer, context)
            elif isinstance(node, ExpressionStatementNode):
                _collect_calls(node.expression, context)
            elif isinstance(node, ReturnStatementNode):
                _collect_calls(node.value, context)
            elif isinstance(node, IfStatementNode):
                _collect_calls(node.condition, context)
                _collect_calls(node.then_block, context)
                if node.else_block:
                    _collect_calls(node.else_block, context)
            elif isinstance(node, ForStatementNode):
                _collect_calls(node.iterable, context)
                _collect_calls(node.body, context)
            elif isinstance(node, BlockNode):
                for child in node.statements:
                    _collect_calls(child, context)
            elif isinstance(node, BinaryExpressionNode):
                _collect_calls(node.left, context)
                _collect_calls(node.right, context)
            elif isinstance(node, UnaryExpressionNode):
                _collect_calls(node.operand, context)

        _collect_declarations(ast)
        _collect_calls(ast)

        # Analyze for forward references
        # A forward reference is when a function calls another function
        # that is defined later in the file (higher line number)
        for caller_context, callee, call_line in calls:
            # Skip if callee is an imported module function
            if "." in callee:
                module_name = callee.split(".")[0]
                if module_name in imports:
                    continue

            # Skip if callee is a stdlib function
            if callee in _STDLIB_FUNCTIONS:
                continue

            # Check if callee is defined in this file
            if callee in function_defs:
                callee_def_line = function_defs[callee]
                # Find the caller's definition line
                caller_def_line = function_defs.get(caller_context, 0)

                # Forward reference: callee is defined after the caller
                if callee_def_line > caller_def_line and caller_context != "global":
                    violations.append(
                        {
                            "type": "forward_reference",
                            "file": str(file_path),
                            "line": call_line,
                            "caller": caller_context,
                            "callee": callee,
                            "module": None,
                        }
                    )

        # Analyze for missing imports
        # A missing import is when a function calls module.function()
        # but the module is not imported
        for caller_context, callee, call_line in calls:
            if "." in callee:
                parts = callee.split(".", 1)
                module_name = parts[0]
                func_name = parts[1]

                # Check if this looks like a module function call
                # (module name is lowercase, function name is lowercase)
                if module_name.islower() and func_name.islower():
                    if module_name not in imports:
                        # Check if it's a stdlib module
                        if module_name in _STDLIB_MODULES:
                            continue
                        # Check if the module exists as a file in the same directory
                        module_file = file_path.parent / f"{module_name}.ail"
                        if module_file.exists():
                            violations.append(
                                {
                                    "type": "missing_import",
                                    "file": str(file_path),
                                    "line": call_line,
                                    "caller": caller_context,
                                    "callee": callee,
                                    "module": module_name,
                                }
                            )

    except Exception:
        # If parsing fails, return empty violations
        pass

    return violations


# Known stdlib functions and modules to skip during checking
_STDLIB_FUNCTIONS = frozenset(
    {
        "math.add",
        "math.sub",
        "math.mul",
        "math.div",
        "math.abs",
        "math.min",
        "math.max",
        "string.concat",
        "string.equals",
        "string.uppercase",
        "string.lowercase",
        "string.length",
        "string.contains",
        "string.starts_with",
        "string.ends_with",
        "string.trim",
        "string.substring",
        "string.find",
        "string.find_from",
        "string.split",
        "list.new",
        "list.append",
        "list.len",
        "list.get",
        "list.contains",
        "list.remove",
        "list.clear",
        "list.sum",
        "list.find_by_key",
        "list.filter_by_key",
        "list.filter_by_contains",
        "list.collect_key",
        "map.new",
        "map.set",
        "map.get",
        "map.has",
        "map.delete",
        "map.keys",
        "map.clear",
        "set.new",
        "set.add",
        "set.contains",
        "set.len",
        "set.remove",
        "set.clear",
        "file.exists",
        "file.read",
        "file.write",
        "file.append",
        "file.remove",
        "file.listdir",
        "path.join",
        "path.basename",
        "path.dirname",
        "path.extension",
        "path.normalize",
        "json.parse",
        "json.stringify",
        "csv.parse",
        "csv.parse_header",
        "csv.stringify",
        "time.now",
        "time.timestamp",
        "time.sleep",
        "time.format",
        "random.int",
        "random.float",
        "random.choice",
        "environment.get",
        "environment.cwd",
        "environment.args",
        "convert.to_string",
        "convert.to_int",
        "convert.to_bool",
        "convert.to_number",
        "io.write",
        "io.writeln",
        "io.println",
        "system.exit",
        "array.new",
        "array.push",
        "array.len",
        "array.get",
        "array.contains",
        "array.remove",
        "array.clear",
    }
)

_STDLIB_MODULES = frozenset(
    {
        "math",
        "string",
        "list",
        "map",
        "set",
        "file",
        "path",
        "json",
        "csv",
        "time",
        "random",
        "environment",
        "convert",
        "io",
        "system",
        "array",
    }
)


# Directories to skip when formatting a project directory
_FMT_SKIP_DIRS = frozenset(
    {
        ".venv",
        ".venv_test",
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "node_modules",
        "__pycache__",
        ".ail",
    }
)


def _collect_ail_files(paths: list[str]) -> list[Path] | None:
    """Resolve file/directory paths to a list of .ail files.

    Returns None if any path doesn't exist (caller handles error message).
    """
    files: list[Path] = []
    for p in paths:
        path = Path(p).resolve()
        if not path.exists():
            return None
        if path.is_dir():
            for found in sorted(path.rglob("*.ail")):
                parts = found.parts
                if any(skip in parts for skip in _FMT_SKIP_DIRS):
                    continue
                files.append(found)
        else:
            files.append(path)
    return files


def _print_diff(filepath: str, original: str, formatted: str) -> None:
    """Print a unified diff of formatting changes to stdout."""
    orig_lines = original.splitlines(keepends=True)
    fmt_lines = formatted.splitlines(keepends=True)
    diff = difflib.unified_diff(
        orig_lines,
        fmt_lines,
        fromfile=f"a/{filepath}",
        tofile=f"b/{filepath}",
    )
    sys.stdout.writelines(diff)


def cmd_fmt(args: list[str]) -> int:
    """Format AILang source files.

    Usage:
        ail fmt <file_or_dir>            Format file(s) in-place
        ail fmt --check <file_or_dir>     Check if formatted (exit 0/1)
        ail fmt --diff <file_or_dir>      Show unified diff of changes
        ail fmt --stdin                   Read from stdin, write formatted
        ail fmt --check --stdin           Check stdin formatting (exit 0/1)
        ail fmt --diff --stdin            Show diff of stdin changes
        ail fmt --quiet <file_or_dir>     Suppress status output
    """
    from compiler.formatter import format_source

    stdin_mode = False
    check_mode = False
    diff_mode = False
    quiet_mode = False
    paths: list[str] = []

    remaining: list[str] = list(args)
    while remaining:
        arg = remaining.pop(0)
        if arg == "--stdin":
            stdin_mode = True
        elif arg == "--check":
            check_mode = True
        elif arg == "--diff":
            diff_mode = True
        elif arg == "--quiet":
            quiet_mode = True
        elif arg.startswith("-"):
            print(f"Unknown option: {arg}", file=sys.stderr)
            print(
                f"Usage: {PROG} fmt [--check] [--diff] [--stdin] [--quiet] "
                f"[<file_or_dir>]",
                file=sys.stderr,
            )
            return 1
        else:
            paths.append(arg)

    # --stdin mode
    if stdin_mode:
        source = sys.stdin.read()
        try:
            formatted = format_source(source)
        except ValueError as e:
            print(f"Format error: {e}", file=sys.stderr)
            return 1
        if check_mode:
            if source == formatted:
                return 0
            print("stdin would be reformatted", file=sys.stderr)
            return 1
        if diff_mode:
            if source == formatted:
                return 0
            _print_diff("stdin", source, formatted)
            return 1
        sys.stdout.write(formatted)
        sys.stdout.flush()
        return 0

    # Path mode (file or directory)
    if not paths:
        print("Error: missing file or directory argument", file=sys.stderr)
        print(
            f"Usage: {PROG} fmt [--check] [--diff] [--stdin] [--quiet] "
            f"[<file_or_dir>]",
            file=sys.stderr,
        )
        return 1

    ail_files = _collect_ail_files(paths)
    if ail_files is None:
        print(f"Error: not found: {paths[0]}", file=sys.stderr)
        return 1

    if not ail_files:
        print(f"Error: no .ail files found in {paths[0]}", file=sys.stderr)
        return 1

    changes = 0
    errors = 0
    for file in ail_files:
        try:
            original = file.read_text(encoding="utf-8")
            formatted = format_source(original)
        except ValueError as e:
            print(f"Format error in {file}: {e}", file=sys.stderr)
            errors += 1
            continue

        if original == formatted:
            continue

        changes += 1

        if check_mode:
            print(f"{file} would be reformatted")
            continue

        if diff_mode:
            _print_diff(str(file), original, formatted)
            continue

        file.write_text(formatted, encoding="utf-8")
        if not quiet_mode:
            print(f"Formatted: {file}")

    if not quiet_mode and len(ail_files) > 1 and not check_mode and not diff_mode:
        if changes or errors:
            print()
        if changes:
            print(f"Formatted {changes} file(s)")
        if errors:
            print(f"{errors} error(s)", file=sys.stderr)
    elif check_mode and changes:
        if not quiet_mode:
            print(f"\n{changes} file(s) would be reformatted")
        return 1
    elif diff_mode and changes:
        if not quiet_mode and changes > 1:
            print(f"\n{changes} file(s) would be reformatted", file=sys.stderr)
        return 1

    return 1 if errors else 0


def cmd_lsp(args: list[str]) -> int:
    """Start the AILang Language Server Protocol server."""
    from compiler.lsp.server import LspServer

    server = LspServer()
    server.run()
    return 0


def cmd_version(args: list[str]) -> int:
    """Print version information."""
    print(_get_version())
    return 0


_NEW_PROJECT_TEMPLATES: dict[str, str] = {
    "main.ail": """\
import file;
import json;
import list;
import map;
import string;

let app_name = "inventory";

fn show_item(item) {
    print("- " + map.get(item, "name"));
}

fn show_all(items, index) {
    if (index < list.len(items)) {
        let item = list.get(items, index);
        show_item(item);
        show_all(items, index + 1);
    }
}

fn main() {
    print("Welcome to " + string.concat(app_name, "!"));
    print("");
    print("Get started by editing main.ail");
    print("");
    if (file.exists("data/sample.json")) {
        let raw = file.read("data/sample.json");
        let items = json.parse(raw);
        print("Loaded sample items:");
        show_all(items, 0);
    }
}
""",
    "config/app.ail": """\
let app_version = "1.0.0";
let debug_mode = false;
""",
    "data/sample.json": """\
[
    {"name": "Widget A", "quantity": 10},
    {"name": "Widget B", "quantity": 5},
    {"name": "Gadget C", "quantity": 2}
]
""",
    "README.md": """\
# Inventory

An AILang project.

## Quick start

    ail run main.ail
""",
}

_TEMPLATE_EMPTY_PROJECT: dict[str, str] = {
    "main.ail": """\
import io;
import string;

fn main() {
    print("Hello from AILang!");
}
""",
    "README.md": """\
# My AILang Project

## Quick start

    ail run main.ail
""",
}

_AIL_TOML_TEMPLATE = """\
[project]
name = "{name}"
version = "0.1.0"
description = "{description}"
entry = "main.ail"

[language]
version = "0.3"
"""

_AIL_LOCK_TEMPLATE = """\
# ail.lock — Auto-generated. Do not edit manually.
"""


def _create_project_dir(project_name: str, templates: dict[str, str]) -> int:
    """Create a project directory from a template dict.

    Also generates ail.toml and ail.lock for package management.
    """
    project_path = Path.cwd() / project_name
    if project_path.exists():
        print(f"Error: directory already exists: {project_path}", file=sys.stderr)
        return 1
    project_path.mkdir(parents=True, exist_ok=False)
    for rel_path, content in templates.items():
        full = project_path / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        print(f"  Created: {full.name}")

    # Generate ail.toml with snake_case package name
    safe_name = project_name.replace("-", "_")
    toml_content = _AIL_TOML_TEMPLATE.format(
        name=safe_name,
        description="An AILang project",
    )
    toml_path = project_path / "ail.toml"
    toml_path.write_text(toml_content, encoding="utf-8")
    print("  Created: ail.toml")

    # Generate ail.lock
    lock_path = project_path / "ail.lock"
    lock_path.write_text(_AIL_LOCK_TEMPLATE, encoding="utf-8")
    print("  Created: ail.lock")

    print(f"\nProject '{project_name}' created in: {project_path}")
    print(f"Run:    cd {project_name} && ail run main.ail")
    return 0


def cmd_new(args: list[str]) -> int:
    """Scaffold a new AILang project.

    Usage:
        ail new <project_name>
        ail new <project_name> --empty      Minimal skeleton (no sample data)
    """
    empty_mode = False
    positional: list[str] = []

    remaining = list(args)
    while remaining:
        arg = remaining.pop(0)
        if arg == "--empty":
            empty_mode = True
        elif arg.startswith("-"):
            print(f"Usage: {PROG} new [--empty] <project_name>", file=sys.stderr)
            return 1
        else:
            positional.append(arg)

    if not positional:
        print("Error: missing project name", file=sys.stderr)
        print(f"Usage: {PROG} new [--empty] <project_name>", file=sys.stderr)
        return 1

    project_name = positional[0]
    if not project_name.replace("-", "_").isidentifier():
        print(f"Error: '{project_name}' is not a valid project name", file=sys.stderr)
        return 1

    templates = _TEMPLATE_EMPTY_PROJECT if empty_mode else _NEW_PROJECT_TEMPLATES
    return _create_project_dir(project_name, templates)


def cmd_pkg_install(args: list[str]) -> int:
    """Install dependencies from ail.toml.

    Delegates to the package manager tool.
    """
    # Add the project root to PYTHONPATH so tools.* is importable
    project_root = _find_stdlib().parent
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    root_str = str(project_root)
    if root_str not in pythonpath:
        env["PYTHONPATH"] = root_str + (";" + pythonpath if pythonpath else "")

    return subprocess.run(
        [sys.executable, "-m", "tools.ail_package_manager", "install"] + list(args),
        env=env,
    ).returncode


def cmd_pkg_add(args: list[str]) -> int:
    """Add a dependency to ail.toml.

    Usage:
        ail add <package>              Add with default version (*)
        ail add <package> --version X  Add with specific version
        ail add <package> --path /loc  Add local dependency
        ail add <package> --git URL    Add git dependency
    """
    project_root = _find_stdlib().parent
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    root_str = str(project_root)
    if root_str not in pythonpath:
        env["PYTHONPATH"] = root_str + (";" + pythonpath if pythonpath else "")

    return subprocess.run(
        [sys.executable, "-m", "tools.ail_package_manager", "add"] + list(args),
        env=env,
    ).returncode


def cmd_pkg_remove(args: list[str]) -> int:
    """Remove a dependency from ail.toml.

    Usage:
        ail remove <package>
    """
    project_root = _find_stdlib().parent
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    root_str = str(project_root)
    if root_str not in pythonpath:
        env["PYTHONPATH"] = root_str + (";" + pythonpath if pythonpath else "")

    return subprocess.run(
        [sys.executable, "-m", "tools.ail_package_manager", "remove"] + list(args),
        env=env,
    ).returncode


def cmd_pkg_update(args: list[str]) -> int:
    """Update dependencies.

    Usage:
        ail update              Update all dependencies
        ail update <package>    Update a specific dependency
    """
    project_root = _find_stdlib().parent
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    root_str = str(project_root)
    if root_str not in pythonpath:
        env["PYTHONPATH"] = root_str + (";" + pythonpath if pythonpath else "")

    return subprocess.run(
        [sys.executable, "-m", "tools.ail_package_manager", "update"] + list(args),
        env=env,
    ).returncode


def cmd_pkg_list(args: list[str]) -> int:
    """List installed dependencies.

    Usage:
        ail list               List all dependencies
        ail list --tree        Show dependency tree
        ail list --outdated    Show outdated packages
    """
    project_root = _find_stdlib().parent
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    root_str = str(project_root)
    if root_str not in pythonpath:
        env["PYTHONPATH"] = root_str + (";" + pythonpath if pythonpath else "")

    return subprocess.run(
        [sys.executable, "-m", "tools.ail_package_manager", "list"] + list(args),
        env=env,
    ).returncode


def cmd_publish(args: list[str]) -> int:
    """Pack and publish the current project to a registry.

    Usage:
        ail publish                      Publish to default registry
        ail publish --registry <url>     Publish to a specific registry
    """
    registry_url: str | None = None
    remaining = list(args)
    while remaining:
        arg = remaining.pop(0)
        if arg == "--registry":
            if remaining:
                registry_url = remaining.pop(0)
            else:
                print("Error: --registry requires a URL argument", file=sys.stderr)
                return 1
        elif arg.startswith("-"):
            print(f"Usage: {PROG} publish [--registry <url>]", file=sys.stderr)
            return 1

    from compiler.package.registry import (
        RegistryError,
        load_registry_url,
        publish_local,
        publish_remote,
    )

    if registry_url is None:
        registry_url = load_registry_url(Path.cwd())

    try:
        if registry_url.startswith(("file://", "/", ".", "\\")):
            local_path = registry_url
            if local_path.startswith("file:///"):
                local_path = local_path[8:]  # file:///C:/... -> C:/...
            elif local_path.startswith("file://"):
                local_path = local_path[7:]  # file://host/path
            publish_local(Path.cwd(), Path(local_path).resolve())
        else:
            publish_remote(Path.cwd(), registry_url)
        return 0
    except (RegistryError, ValueError) as e:
        print(f"Publish error: {e}", file=sys.stderr)
        return 1


def cmd_test(args: list[str]) -> int:
    """Discover and run test files (test_*.ail).

    Automatically runs ail check before test discovery to detect
    forward references, missing imports, and ordering violations.
    If check fails, tests do not run — developer receives exact fixes.

    Each test file must define a main() function that calls test functions
    and prints results. A test passes if it compiles and runs without output
    containing "FAIL".

    Usage:
        ail test                         Run all tests in current directory
        ail test <file_or_dir>           Run tests in specific file/directory
        ail test --verbose               Print per-test names and output
        ail test --root <dir>            Set project root for module resolution
        ail test --no-check              Skip pre-flight ordering check

    Examples:
        # Run tests in current project
        ail test

        # Run tests for a specific application
        ail test --root apps/inventory

        # Run tests from application directory
        cd apps/inventory
        ail test

        # Run a specific test file
        ail test apps/inventory/tests/test_supplier.ail

    Supported Patterns:
        - test_*.ail
        - *_test.ail

    Excluded Directories:
        - .ail/ (internal backups)
        - backups/
        - __pycache__/
        - dist/
        - build/
        - .git/
        - node_modules/
        - .venv/
    """
    import io

    verbose = False
    no_check = False
    root_override: str | None = None
    paths: list[str] = []

    remaining = list(args)
    while remaining:
        arg = remaining.pop(0)
        if arg == "--verbose":
            verbose = True
        elif arg == "--no-check":
            no_check = True
        elif arg == "--root":
            if remaining:
                root_override = remaining.pop(0)
            else:
                print("Error: --root requires a directory argument", file=sys.stderr)
                return 1
        elif arg.startswith("-"):
            print(
                f"Usage: {PROG} test [--verbose] [--no-check] [--root <dir>] [<file_or_dir>]",
                file=sys.stderr,
            )
            return 1
        else:
            paths.append(arg)

    # Default root to CWD so 'ail test tests/' resolves modules from CWD
    if root_override is None:
        root_override = str(Path.cwd())

    # Directories to exclude from test discovery
    _TEST_EXCLUDE_DIRS = {
        ".ail",
        "backups",
        "__pycache__",
        "dist",
        "build",
        ".git",
        "node_modules",
        ".venv",
        ".venv_test",
    }

    def _should_exclude_path(path: Path) -> bool:
        """Check if a path should be excluded from test discovery."""
        for part in path.parts:
            if part in _TEST_EXCLUDE_DIRS:
                return True
        return False

    # Collect test files
    patterns = ["test_*.ail", "*_test.ail"]
    test_files_set: set[Path] = set()
    if not paths:
        root = Path.cwd()
        for pattern in patterns:
            for f in sorted(root.rglob(pattern)):
                if not _should_exclude_path(f):
                    test_files_set.add(f)
        if not test_files_set:
            print("No tests found", file=sys.stderr)
            print("Supported patterns:", file=sys.stderr)
            print("- test_*.ail", file=sys.stderr)
            print("- *_test.ail", file=sys.stderr)
            return 1
    else:
        for p in paths:
            path = Path(p).resolve()
            if not path.exists():
                print(f"Error: not found: {path}", file=sys.stderr)
                return 1
            if path.is_dir():
                for pattern in patterns:
                    for f in sorted(path.rglob(pattern)):
                        if not _should_exclude_path(f):
                            test_files_set.add(f)
            elif path.suffix == ".ail":
                test_files_set.add(path)
            else:
                print(f"Error: not an .ail file: {path}", file=sys.stderr)
                return 1

    test_files = sorted(test_files_set)
    if not test_files:
        print("No tests found", file=sys.stderr)
        print("Supported patterns:", file=sys.stderr)
        print("- test_*.ail", file=sys.stderr)
        print("- *_test.ail", file=sys.stderr)
        return 1

    # Auto-check: detect forward references and ordering violations before test execution
    if not no_check:
        all_violations: list[dict] = []
        for test_file in test_files:
            violations = _check_file_forward_references(test_file)
            all_violations.extend(violations)

        if all_violations:
            formatter = DiagnosticFormatter()
            for v in all_violations:
                print()
                if v["type"] == "forward_reference":
                    print("FORWARD_REF:")
                elif v["type"] == "missing_import":
                    print("MISSING_IMPORT:")
                print(f"{v['file']}:{v['line']}")
                print()
                print(f"  {v['caller']}()")
                print(f"  calls {v['callee']}()")
                print()
                print("  Suggestion:")
                if v["type"] == "forward_reference":
                    print(f"    Move {v['callee']}() definition above {v['caller']}()")
                elif v["type"] == "missing_import":
                    print(f"    Add: import {v['module']};")
                print()
            print(f"Check failed: {len(all_violations)} violation(s) found.")
            print(
                "Fix these issues before running tests. Use --no-check to skip.",
                file=sys.stderr,
            )
            return 1

    total = len(test_files)
    passed = 0
    failed = 0
    errors: list[str] = []

    for test_file in test_files:
        session, reporter = _compile(test_file, root_override=root_override)
        if session is None:
            failed += 1
            errors.append(test_file.name)
            print(f"FAIL  {test_file.name} (compile error)", file=sys.stderr)
            if verbose:
                formatter = DiagnosticFormatter()
                for diagnostic in reporter.diagnostics:
                    print("  " + formatter.format(diagnostic), file=sys.stderr)

            # Check for common import-related errors and provide guidance
            has_import_error = False
            suggested_root = None
            for diagnostic in reporter.diagnostics:
                msg = getattr(diagnostic, "message", "")
                if "Symbol not found in module" in msg or "Undefined identifier" in msg:
                    # Check if this looks like an app-local import
                    file_path = Path(test_file)
                    parts = file_path.parts
                    # Look for apps/<app_name>/tests/ pattern
                    if "apps" in parts and "tests" in parts:
                        apps_idx = parts.index("apps")
                        tests_idx = parts.index("tests")
                        if tests_idx > apps_idx:
                            app_name = parts[apps_idx + 1]
                            suggested_root = f"apps/{app_name}"
                            has_import_error = True

            if has_import_error and suggested_root:
                print(
                    "\n  Hint: This appears to be an application-local import.",
                    file=sys.stderr,
                )
                print("  Try running with --root flag:", file=sys.stderr)
                print(f"    ail test --root {suggested_root}", file=sys.stderr)
                print("  Or run from the application directory:", file=sys.stderr)
                print(f"    cd {suggested_root}", file=sys.stderr)
                print("    ail test", file=sys.stderr)
            continue

        # Execute the test file
        bundle = session.build_ir()
        runtime = Runtime(bundle)

        for module_name in session._graph.topological_sort():
            runtime._initialize_module(module_name)

        try:
            main_module = None
            for module_name in session._graph.topological_sort():
                if module_name in bundle.module_irs:
                    main_module = module_name
                    break

            if main_module is None:
                raise KeyError("No module found")

            program_ir = bundle.module_irs[main_module]

            old_stdout = sys.stdout
            sys.stdout = captured = io.StringIO()
            try:
                runtime.execute(program_ir)
            finally:
                sys.stdout = old_stdout

            output = captured.getvalue()
            has_fail = "FAIL" in output

            if has_fail:
                failed += 1
                errors.append(test_file.name)
                print(f"FAIL  {test_file.name}", file=sys.stderr)
                if verbose:
                    for line in output.strip().split("\n"):
                        print("  " + line, file=sys.stderr)
            else:
                passed += 1
                if verbose:
                    print(f"PASS  {test_file.name}")
                    if output.strip():
                        for line in output.strip().split("\n"):
                            print("  " + line)

        except Exception as e:
            failed += 1
            errors.append(test_file.name)
            print(f"FAIL  {test_file.name} (runtime error: {e})", file=sys.stderr)

    print(
        f"\nTest results: {passed}/{total} passed",
        file=sys.stderr if failed else sys.stdout,
    )
    if failed:
        print(f"Failed: {', '.join(errors)}", file=sys.stderr)
    return 1 if failed else 0


def cmd_order(args: list[str]) -> int:
    """Run the dependency ordering assistant."""
    return subprocess.run(
        [sys.executable, "-m", "tools.ail_order"] + list(args)
    ).returncode


def cmd_rename(args: list[str]) -> int:
    """Rename an identifier repository-wide.

    Usage:
        ail rename <old_name> <new_name>
        ail rename --dry-run <old_name> <new_name>
        ail rename --diff <old_name> <new_name>
        ail rename --strings <old_name> <new_name>
        ail rename --no-verify <old_name> <new_name>
    """
    from compiler.rename import RenameTool

    dry_run = False
    diff_mode = False
    include_strings = False
    no_verify = False
    positional: list[str] = []

    remaining = list(args)
    while remaining:
        arg = remaining.pop(0)
        if arg == "--dry-run":
            dry_run = True
        elif arg == "--diff":
            diff_mode = True
        elif arg == "--strings":
            include_strings = True
        elif arg == "--no-verify":
            no_verify = True
        elif arg.startswith("-"):
            print(
                f"Usage: {PROG} rename [--dry-run] [--diff] [--strings] [--no-verify] <old_name> <new_name>",
                file=sys.stderr,
            )
            return 1
        else:
            positional.append(arg)

    if len(positional) != 2:
        print(f"Usage: {PROG} rename [options] <old_name> <new_name>", file=sys.stderr)
        return 1

    old_name = positional[0]
    new_name = positional[1]

    if not new_name.isidentifier():
        print(f"Error: '{new_name}' is not a valid AILang identifier", file=sys.stderr)
        return 4

    root_dir = _find_stdlib().parent
    tool = RenameTool(root_dir)

    refs = tool.scan(old_name, include_strings=include_strings)
    if not refs:
        print(f"No references found for '{old_name}'", file=sys.stderr)
        return 2

    changes = tool.compute_changes(old_name, new_name)
    if not changes:
        print(f"No files to change for '{old_name}' → '{new_name}'", file=sys.stderr)
        return 0

    if dry_run or diff_mode:
        for file_path, change in sorted(changes.items()):
            if diff_mode:
                pass  # print diff below
            else:
                print(f"  {file_path}")

        if diff_mode:
            tool.print_diff(changes)

        plural = "s" if len(changes) > 1 else ""
        print(f"\n{len(changes)} file{plural} would be modified")
        return 0

    try:
        rb_dir = tool.apply(changes)
    except BaseException as e:
        print(f"Error during rename: {e}", file=sys.stderr)
        print("All changes have been rolled back.", file=sys.stderr)
        return 1

    print(f"Renamed '{old_name}' → '{new_name}' across {len(changes)} file(s)")
    print(f"Rollback bundle: {rb_dir}")

    if not no_verify:
        entry = root_dir / "main.ail"
        if not entry.exists():
            ail_files = sorted(root_dir.rglob("*.ail"))
            entry = ail_files[0] if ail_files else root_dir
        print("Verifying with compiler...")
        ok = tool.verify(str(entry))
        if ok:
            print("Verification: PASSED")
        else:
            print("Verification: FAILED — check for errors above", file=sys.stderr)
            return 3

    return 0


def cmd_watch(args: list[str]) -> int:
    """Watch for file changes and recompile incrementally.

    Usage:
        ail watch [<entry_file>]
        ail watch --poll
        ail watch --json
        ail watch --no-initial
    """
    from compiler.watch import run_watch

    poll = False
    poll_interval = 500
    no_initial = False
    json_mode = False
    verbose = False
    positional: list[str] = []

    remaining = list(args)
    while remaining:
        arg = remaining.pop(0)
        if arg == "--poll":
            poll = True
        elif arg == "--json":
            json_mode = True
        elif arg == "--no-initial":
            no_initial = True
        elif arg == "--verbose":
            verbose = True
        elif arg.startswith("--poll-interval"):
            if "=" in arg:
                poll_interval = int(arg.split("=")[1])
            else:
                poll_interval = int(remaining.pop(0))
        elif arg.startswith("-"):
            print(
                f"Usage: {PROG} watch [--poll] [--json] [--no-initial] [<file>]",
                file=sys.stderr,
            )
            return 1
        else:
            positional.append(arg)

    entry_path = positional[0] if positional else "."
    entry = Path(entry_path).resolve()
    if not entry.exists():
        print(f"Error: not found: {entry}", file=sys.stderr)
        return 1

    return run_watch(
        str(entry),
        poll=poll,
        poll_interval=poll_interval,
        no_initial=no_initial,
        json_mode=json_mode,
        verbose=verbose,
    )


def _run_dx_tool(module_name: str, args: list[str]) -> int:
    """Helper to run a DX tool by shelling out to its __main__ module."""
    project_root = _find_stdlib().parent
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    root_str = str(project_root)
    if root_str not in pythonpath:
        env["PYTHONPATH"] = root_str + (";" + pythonpath if pythonpath else "")
    return subprocess.run(
        [sys.executable, "-m", module_name] + list(args),
        env=env,
    ).returncode


def cmd_heal(args: list[str]) -> int:
    """Get fix suggestions for common errors.

    Usage:
        ail heal                  List available topics
        ail heal <topic>          Show fix suggestions for a topic
    """
    return _run_dx_tool("tools.ail_heal", args)


def cmd_explain(args: list[str]) -> int:
    """Explain a compiler error code in detail.

    Usage:
        ail explain              List all known error codes
        ail explain <CODE>       Show detailed explanation for CODE

    Examples:
        ail explain TYP001
        ail explain SEM002
        ail explain MOD004
    """
    from compiler.cli.explain import explain, list_codes

    if not args or args[0] in ("-h", "--help"):
        print(list_codes())
        return 0

    code = args[0].upper()
    result = explain(code)
    if result is None:
        print(f"Unknown error code: {args[0]}", file=sys.stderr)
        print("Run 'ail explain' to see all known codes.", file=sys.stderr)
        return 1
    print(result)
    return 0


def cmd_doctor(args: list[str]) -> int:
    """Run repository health checks.

    Usage:
        ail doctor
    """
    return _run_dx_tool("tools.ail_doctor", args)


def cmd_docs(args: list[str]) -> int:
    """Retrieve AILang documentation without filesystem access.

    Usage:
        ail docs                  List available documents
        ail docs <name>           Print document content
        ail docs --json           Machine-readable output
    """
    return _run_dx_tool("tools.ail_docs", args)


def cmd_context(args: list[str]) -> int:
    """Generate AI-friendly project context.

    Usage:
        ail context          Generate PROJECT_CONTEXT.md (human-readable)
        ail context --json   Output machine-readable JSON to stdout
    """
    return _run_dx_tool("tools.ail_context", args)


def cmd_static_analyzer(args: list[str]) -> int:
    """Run static analysis on AILang source files.

    Usage:
        ail static-analyzer [<target>] [options]
    """
    return _run_dx_tool("tools.ail_static_analyzer", args)


def cmd_benchmark(args: list[str]) -> int:
    """Run the AILang benchmark suite.

    Usage:
        ail benchmark [options]
    """
    return _run_dx_tool("tools.ail_benchmark", args)


def cmd_testgen(args: list[str]) -> int:
    """Generate test cases for AILang applications.

    Usage:
        ail testgen [options]
    """
    return _run_dx_tool("tools.ail_testgen", args)


def cmd_mcp(args: list[str]) -> int:
    """Start the AILang MCP server on stdio transport.

    Usage:
        ail mcp

    Starts a Model Context Protocol server that exposes AILang compiler
    capabilities to AI tools via stdio transport.
    """
    return _run_dx_tool("tools.ail_mcp", args)


def cmd_help(args: list[str]) -> int:
    """Print help information."""
    print(_get_version())
    print()
    print("Usage:")
    print(f"  {PROG} [options]")
    print(f"  {PROG} <command> [args]")
    print()
    print("Options:")
    print("  -h, --help          Show this help message")
    print("  -v, --version       Show version information")
    print()
    print("Commands:")
    print("  run <file>          Compile and run an AILang program")
    print("  build <file>        Compile and check for errors (no execution)")
    print("  check <file>        Check for forward references and ordering violations")
    print("  fmt <file_or_dir>   Format AILang source file(s)")
    print("  test [<file_or_dir>] Run test_*.ail files")
    print("  new <project>       Create a new AILang project scaffold")
    print("  rename <old> <new>  Rename identifier repository-wide")
    print("  watch [<file>]      Watch for changes, recompile incrementally")
    print("  order <target>      Analyze dependency ordering of .ail files")
    print()
    print("Package Management:")
    print("  install             Install dependencies from ail.toml")
    print("  add <package>       Add a dependency to ail.toml")
    print("  remove <package>    Remove a dependency from ail.toml")
    print("  update              Re-resolve all dependencies")
    print("  list                List installed dependencies")
    print("  publish             Publish project to package registry")
    print()
    print("Developer Tools:")
    print("  doctor              Run repository health checks")
    print("  heal                Get fix suggestions for common errors")
    print("  explain <CODE>      Explain a compiler error code in detail")
    print("  docs [<name>]       Retrieve AILang documentation (no filesystem access)")
    print(
        "  context [--json]    Generate AI-friendly project context (use --json for machine-readable)"
    )
    print(
        "  mcp                 Start MCP server for AI tool integration (stdio transport)"
    )
    print("  static-analyzer     Run static analysis on AILang source")
    print("  benchmark           Run the AILang benchmark suite")
    print("  testgen             Generate test cases for AILang apps")
    print()
    print("Other:")
    print("  lsp                 Start the LSP server (stdin/stdout)")
    print("  version             Print version information")
    print("  help                Print this help message")
    print()
    print("Examples:")
    print(f"  {PROG} run hello.ail")
    print(f"  {PROG} build hello.ail")
    print(f"  {PROG} fmt hello.ail")
    print(f"  {PROG} test tests/")
    print(f"  {PROG} new myproject")
    print(f"  {PROG} doctor")
    print(f"  {PROG} --version")
    print(f"  {PROG} --help")
    print()
    print("New to AILang?")
    print()
    print("Recommended workflow:")
    print()
    print(f"  {PROG} doctor              # 1. Check your environment")
    print(f"  {PROG} docs AGENTS         # 2. Read the AI agent instructions")
    print(f"  {PROG} context --json      # 3. Get machine-readable language context")
    print(f"  {PROG} fmt                 # 4. Format your code")
    print(f"  {PROG} check               # 5. Validate before building")
    print(f"  {PROG} build               # 6. Compile and check for errors")
    print(f"  {PROG} run                 # 7. Compile and execute")
    return 0


# =============================================================================
# Subcommand dispatch table
# =============================================================================


def main(argv: list[str] | None = None) -> int:
    """Main entry point. Parses args and dispatches to the appropriate command.

    Supports global --dev flag in two positions:
        ail --dev <command>
        ail <command> --dev
    """
    commands: dict[str, Callable[[list[str]], int]] = {
        "run": cmd_run,
        "build": cmd_build,
        "check": cmd_check,
        "fmt": cmd_fmt,
        "new": cmd_new,
        "test": cmd_test,
        "install": cmd_pkg_install,
        "add": cmd_pkg_add,
        "remove": cmd_pkg_remove,
        "update": cmd_pkg_update,
        "list": cmd_pkg_list,
        "publish": cmd_publish,
        "lsp": cmd_lsp,
        "order": cmd_order,
        "rename": cmd_rename,
        "watch": cmd_watch,
        "version": cmd_version,
        "help": cmd_help,
        "doctor": cmd_doctor,
        "heal": cmd_heal,
        "explain": cmd_explain,
        "docs": cmd_docs,
        "context": cmd_context,
        "mcp": cmd_mcp,
        "static-analyzer": cmd_static_analyzer,
        "static_analyzer": cmd_static_analyzer,
        "benchmark": cmd_benchmark,
        "testgen": cmd_testgen,
    }

    # Check for first run (skip for version/help/help flags)
    if argv is None:
        argv = sys.argv[1:]

    skip_first_run_check = not argv or argv[0] in (
        "-v",
        "--version",
        "-h",
        "--help",
        "help",
        "version",
    )

    if not skip_first_run_check and _is_first_run():
        _show_welcome()

    if not argv:
        cmd_help([])
        return 1

    # Parse global --dev flag (supports both positions: ail --dev CMD and ail CMD --dev)
    dev_mode_requested = False
    new_argv = []
    i = 0
    while i < len(argv):
        if argv[i] == "--dev":
            dev_mode_requested = True
            i += 1
            continue
        new_argv.append(argv[i])
        i += 1

    if dev_mode_requested:
        # Set the global dev mode flag for _find_stdlib() to use
        import compiler.cli.main as cli_module

        cli_module._DEV_MODE = True

    argv = new_argv

    command = argv[0]
    rest = argv[1:]

    # Global flags
    if command in ("-v", "--version"):
        print(_get_version())
        return 0
    if command in ("-h", "--help"):
        cmd_help([])
        return 0

    # Check if the first argument is a known subcommand
    if command in commands:
        handler = commands[command]
        return handler(rest)

    # Otherwise treat it as a file -> shorthand for `run`
    return cmd_run(argv)


if __name__ == "__main__":
    sys.exit(main())

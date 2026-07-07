#!/usr/bin/env python
"""AILang CLI entry point — the `ail` command.

Usage:
    ail run <file>       Compile and run an AILang program
    ail build <file>     Compile and check for errors (no execution)
    ail check <file>     Compile and check for errors (alias for build)
    ail version          Print version information
    ail help             Print this help message
    ail <file>           Shorthand for `ail run <file>`
"""

from __future__ import annotations

import difflib
import sys
from collections.abc import Callable
from pathlib import Path

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticFormatter, DiagnosticReporter
from compiler.runtime import builtins as runtime_builtins
from compiler.runtime.interpreter import Runtime

PROG = "ail"
VERSION = "0.2.0"


def _find_stdlib() -> Path:
    """Locate the stdlib directory, checking installed package first,
    then falling back to development-tree lookup."""
    # Installed package: stdlib is next to the compiler package
    pkg_dir = Path(__file__).resolve().parent.parent.parent
    candidate = pkg_dir / "stdlib"
    if candidate.is_dir():
        return candidate
    # Development tree: walk up from CWD or package path
    for start in [Path.cwd(), pkg_dir]:
        current = start
        while True:
            if (current / "stdlib").is_dir() and (current / "pyproject.toml").is_file():
                return current / "stdlib"
            if current == current.parent:
                break
            current = current.parent
    return pkg_dir / "stdlib"


def _get_version() -> str:
    return f"AILang v{VERSION}"


# =============================================================================
# Command implementations
# =============================================================================


def _compile(source_path: Path) -> CompilationSession | None:
    """Compile a source file and return the session, or None on error."""
    if not source_path.exists():
        print(f"Error: File not found: {source_path}", file=sys.stderr)
        return None

    stdlib_dir = _find_stdlib()
    root_dir = stdlib_dir.parent

    session = CompilationSession()
    session._root = root_dir
    session._resolver = type(session._resolver)(root_dir)

    reporter = DiagnosticReporter()
    try:
        session.discover(source_path)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

    session.analyze(reporter)

    if reporter.error_count > 0:
        formatter = DiagnosticFormatter()
        for diagnostic in reporter.diagnostics:
            print(formatter.format(diagnostic), file=sys.stderr)
        return None

    return session


def cmd_run(args: list[str]) -> int:
    """Compile and run an AILang program."""
    if not args:
        print("Error: missing file argument", file=sys.stderr)
        print(f"Usage: {PROG} run <file>", file=sys.stderr)
        return 1

    source_path = Path(args[0]).resolve()

    # Strip CLI plumbing so env_args() returns only the user's args.
    # args[0] is the source file; everything after is user-provided.
    runtime_builtins._program_argv = args[1:]

    session = _compile(source_path)
    if session is None:
        return 1

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
        runtime.execute(program_ir)
        return 0
    except Exception as e:
        print(f"Runtime error: {e}", file=sys.stderr)
        return 1


def cmd_build(args: list[str]) -> int:
    """Compile an AILang program and check for errors (no execution)."""
    if not args:
        print("Error: missing file argument", file=sys.stderr)
        print(f"Usage: {PROG} build <file>", file=sys.stderr)
        return 1

    source_path = Path(args[0]).resolve()
    session = _compile(source_path)
    if session is None:
        return 1

    print(f"Build successful: {source_path}")
    return 0


def cmd_check(args: list[str]) -> int:
    """Alias for build — compile and check for errors."""
    return cmd_build(args)


# Directories to skip when formatting a project directory
_FMT_SKIP_DIRS = frozenset({
    ".venv", ".venv_test", ".git", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", "node_modules", "__pycache__", ".ail",
})


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
        orig_lines, fmt_lines,
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


def cmd_help(args: list[str]) -> int:
    """Print help information."""
    print(_get_version())
    print()
    print("Usage:")
    print(f"  {PROG} run <file>       Compile and run an AILang program")
    print(f"  {PROG} build <file>     Compile and check for errors (no execution)")
    print(f"  {PROG} check <file>     Compile and check for errors (alias for build)")
    print(f"  {PROG} fmt <file_or_dir>  Format AILang source file(s)")
    print(f"  {PROG} fmt --check       Check formatting (exit 0/1)")
    print(f"  {PROG} fmt --diff        Show unified diff of formatting changes")
    print(f"  {PROG} fmt --stdin       Read from stdin, write formatted to stdout")
    print(f"  {PROG} fmt --quiet       Suppress status output")
    print(f"  {PROG} lsp              Start the LSP server (stdin/stdout)")
    print(f"  {PROG} version          Print version information")
    print(f"  {PROG} help             Print this help message")
    print()
    print("Examples:")
    print(f"  {PROG} run hello.ail")
    print(f"  {PROG} build hello.ail")
    print(f"  {PROG} fmt hello.ail")
    print(f"  {PROG} fmt --check hello.ail")
    print(f"  {PROG} fmt --diff hello.ail")
    print(f"  {PROG} fmt apps/")
    print(f"  {PROG} fmt --check apps/ stdlib/")
    print(f"  {PROG} version")
    print(f"  {PROG} hello.ail")
    return 0


# =============================================================================
# Subcommand dispatch table
# =============================================================================


def main(argv: list[str] | None = None) -> int:
    """Main entry point. Parses args and dispatches to the appropriate command."""
    commands: dict[str, Callable[[list[str]], int]] = {
        "run": cmd_run,
        "build": cmd_build,
        "check": cmd_check,
        "fmt": cmd_fmt,
        "lsp": cmd_lsp,
        "version": cmd_version,
        "help": cmd_help,
    }

    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        cmd_help([])
        return 1

    command = argv[0]
    rest = argv[1:]

    # Check if the first argument is a known subcommand
    if command in commands:
        handler = commands[command]
        return handler(rest)

    # If the argument looks like a flag (--xxx), show help
    if command.startswith("-"):
        cmd_help([])
        return 1

    # Otherwise treat it as a file -> shorthand for `run`
    return cmd_run(argv)


if __name__ == "__main__":
    sys.exit(main())

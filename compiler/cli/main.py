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
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticFormatter, DiagnosticReporter
from compiler.runtime import builtins as runtime_builtins
from compiler.runtime.interpreter import Runtime

PROG = "ail"
VERSION = "0.10.0"


def _find_stdlib() -> Path:
    """Locate the stdlib directory.

    Order:
    1. Next to the compiler package (works for installed non-editable wheels).
    2. Next to the compiler package parent (works for dev-tree editable installs).
    3. Walk up from CWD looking for stdlib + pyproject.toml (works when run from repo).
    4. Fallback to a bundled path inside site-packages (post-install copy).
    5. Last resort: stdlib next to the compiler package root.
    """
    # Path of the current file = compiler/cli/main.py
    this_file = Path(__file__).resolve()
    pkg_dir = this_file.parent.parent.parent  # site-packages/ or repo root

    # 1. Check next to the compiler package (installed wheel: site-packages/stdlib/)
    candidate = pkg_dir / "stdlib"
    if candidate.is_dir() and any(candidate.iterdir()):
        return candidate

    # 2. Check next to the compiler package parent (dev tree: repo-root/)
    parent_candidate = pkg_dir.parent / "stdlib"
    if parent_candidate.is_dir() and any(parent_candidate.iterdir()):
        return parent_candidate

    # 3. Walk up from CWD
    for start in [Path.cwd(), pkg_dir]:
        current = start
        while True:
            if (current / "stdlib").is_dir() and (current / "pyproject.toml").is_file():
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
    return f"AILang v{VERSION}"


# =============================================================================
# Command implementations
# =============================================================================


def _compile(
    source_path: Path,
    json_mode: bool = False,
    experimental_loops: bool = False,
) -> tuple[CompilationSession | None, DiagnosticReporter]:
    """Compile a source file and return the session and reporter.

    Returns:
        tuple of (session, reporter) where session is None on error.
    """
    if not source_path.exists():
        print(f"Error: File not found: {source_path}", file=sys.stderr)
        return None, DiagnosticReporter()

    stdlib_dir = _find_stdlib()
    root_dir = stdlib_dir.parent

    session = CompilationSession(experimental_loops=experimental_loops)
    # Set root to the source file's directory so app modules are found.
    # Stdlib discovery walks upward from _root, so stdlib/ at the project
    # root is still located.
    session._root = source_path.parent.resolve()
    session._resolver = type(session._resolver)(source_path.parent.resolve())

    reporter = DiagnosticReporter()
    session.discover(source_path, reporter)

    session.analyze(reporter)

    if reporter.error_count > 0:
        if not json_mode:
            formatter = DiagnosticFormatter()
            for diagnostic in reporter.diagnostics:
                print(formatter.format(diagnostic), file=sys.stderr)
        return None, reporter

    return session, reporter


def cmd_run(args: list[str]) -> int:
    """Compile and run an AILang program."""
    experimental_loops = False
    positional: list[str] = []

    remaining = list(args)
    while remaining:
        arg = remaining.pop(0)
        if arg == "--experimental-loops":
            experimental_loops = True
        elif arg.startswith("-"):
            print(f"Usage: {PROG} run [--experimental-loops] <file>", file=sys.stderr)
            return 1
        else:
            positional.append(arg)

    if not positional:
        print("Error: missing file argument", file=sys.stderr)
        print(f"Usage: {PROG} run [--experimental-loops] <file>", file=sys.stderr)
        return 1

    source_path = Path(positional[0]).resolve()

    # Strip CLI plumbing so env_args() returns only the user's args.
    # args[0] is the source file; everything after is user-provided.
    runtime_builtins._program_argv = positional[1:]

    session, _ = _compile(source_path, experimental_loops=experimental_loops)
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
            print(f"Usage: {PROG} build [--json] [--experimental-loops] <file>", file=sys.stderr)
            return 1
        else:
            paths.append(arg)

    if not paths:
        print("Error: missing file argument", file=sys.stderr)
        print(f"Usage: {PROG} build [--json] [--experimental-loops] <file>", file=sys.stderr)
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
"""
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
"""
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
        description=f"An AILang project",
    )
    toml_path = project_path / "ail.toml"
    toml_path.write_text(toml_content, encoding="utf-8")
    print(f"  Created: ail.toml")

    # Generate ail.lock
    lock_path = project_path / "ail.lock"
    lock_path.write_text(_AIL_LOCK_TEMPLATE, encoding="utf-8")
    print(f"  Created: ail.lock")

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
        load_registry_url, publish_local, publish_remote, RegistryError,
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

    Usage:
        ail test                         Run all tests in current directory
        ail test <file_or_dir>           Run tests in specific file/directory
        ail test --verbose               Print per-test names
    """
    verbose = False
    paths: list[str] = []

    remaining = list(args)
    while remaining:
        arg = remaining.pop(0)
        if arg == "--verbose":
            verbose = True
        elif arg.startswith("-"):
            print(f"Usage: {PROG} test [--verbose] [<file_or_dir>]", file=sys.stderr)
            return 1
        else:
            paths.append(arg)

    # Collect test files
    test_files: list[Path] = []
    if not paths:
        root = Path.cwd()
        for f in sorted(root.glob("test_*.ail")):
            test_files.append(f)
        if not test_files:
            print("No test_*.ail files found", file=sys.stderr)
            return 1
    else:
        for p in paths:
            path = Path(p).resolve()
            if not path.exists():
                print(f"Error: not found: {path}", file=sys.stderr)
                return 1
            if path.is_dir():
                for f in sorted(path.glob("test_*.ail")):
                    test_files.append(f)
            elif path.suffix == ".ail":
                test_files.append(path)
            else:
                print(f"Error: not an .ail file: {path}", file=sys.stderr)
                return 1

    if not test_files:
        print("No test files found", file=sys.stderr)
        return 1

    total = len(test_files)
    passed = 0
    failed = 0

    for test_file in test_files:
        session, reporter = _compile(test_file)
        if session is None:
            failed += 1
            print(f"FAIL  {test_file.name}", file=sys.stderr)
            if verbose:
                formatter = DiagnosticFormatter()
                for diagnostic in reporter.diagnostics:
                    print("  " + formatter.format(diagnostic), file=sys.stderr)
        else:
            passed += 1
            if verbose:
                print(f"PASS  {test_file.name}")

    print(f"\nTest results: {passed}/{total} passed",
          file=sys.stderr if failed else sys.stdout)
    return 1 if failed else 0


def cmd_order(args: list[str]) -> int:
    """Run the dependency ordering assistant."""
    return subprocess.run([sys.executable, "-m", "tools.ail_order"] + list(args)).returncode


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
            print(f"Usage: {PROG} rename [--dry-run] [--diff] [--strings] [--no-verify] <old_name> <new_name>", file=sys.stderr)
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
            print(f"Usage: {PROG} watch [--poll] [--json] [--no-initial] [<file>]", file=sys.stderr)
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


def cmd_help(args: list[str]) -> int:
    """Print help information."""
    print(_get_version())
    print()
    print("Usage:")
    print(f"  {PROG} run <file>         Compile and run an AILang program")
    print(f"  {PROG} run --experimental-loops <file>")
    print(f"  {PROG} build <file>       Compile and check for errors (no execution)")
    print(f"  {PROG} build --json       Compile and output JSON diagnostics")
    print(f"  {PROG} build --experimental-loops <file>")
    print(f"  {PROG} check <file>       Compile and check for errors (alias for build)")
    print(f"  {PROG} fmt <file_or_dir>  Format AILang source file(s)")
    print(f"  {PROG} fmt --check       Check formatting (exit 0/1)")
    print(f"  {PROG} fmt --diff        Show unified diff of formatting changes")
    print(f"  {PROG} fmt --stdin       Read from stdin, write formatted to stdout")
    print(f"  {PROG} fmt --quiet       Suppress status output")
    print(f"  {PROG} order <target>    Analyze dependency ordering of .ail files")
    print(f"  {PROG} order --json      Output machine-readable JSON")
    print(f"  {PROG} order --fix       Apply automatic reordering")
    print(f"  {PROG} rename <old> <new>  Rename identifier repository-wide")
    print(f"  {PROG} rename --dry-run   Preview rename without modifying")
    print(f"  {PROG} rename --diff      Show unified diff of rename changes")
    print(f"  {PROG} rename --strings   Also rename string literal values")
    print(f"  {PROG} rename --no-verify Skip compiler verification after rename")
    print(f"  {PROG} watch [<file>]    Watch for changes, recompile incrementally")
    print(f"  {PROG} watch --poll      Use polling instead of filesystem events")
    print(f"  {PROG} watch --json      Machine-readable JSON output")
    print(f"  {PROG} watch --no-initial Skip initial build")
    print(f"  {PROG} new <project>     Create a new AILang project scaffold")
    print(f"  {PROG} new --empty <project>  Minimal scaffold (no sample data)")
    print(f"  {PROG} test              Run all test_*.ail files")
    print(f"  {PROG} test --verbose    Show per-test pass/fail details")
    print(f"  {PROG} install           Install dependencies from ail.toml")
    print(f"  {PROG} install --offline Install from local cache only")
    print(f"  {PROG} add <package>     Add a dependency to ail.toml")
    print(f"  {PROG} add <pkg> --version X   Add with specific version")
    print(f"  {PROG} add <pkg> --path /loc    Add local dependency")
    print(f"  {PROG} remove <package>  Remove a dependency from ail.toml")
    print(f"  {PROG} update            Re-resolve all dependencies")
    print(f"  {PROG} update <package>  Re-resolve a specific dependency")
    print(f"  {PROG} list              List installed dependencies")
    print(f"  {PROG} publish           Publish project to package registry")
    print(f"  {PROG} publish --registry <url>  Publish to custom registry")
    print(f"  {PROG} lsp              Start the LSP server (stdin/stdout)")
    print(f"  {PROG} version          Print version information")
    print(f"  {PROG} help             Print this help message")
    print()
    print("Examples:")
    print(f"  {PROG} run hello.ail")
    print(f"  {PROG} build hello.ail")
    print(f"  {PROG} build --json hello.ail")
    print(f"  {PROG} fmt hello.ail")
    print(f"  {PROG} fmt --check hello.ail")
    print(f"  {PROG} fmt --diff hello.ail")
    print(f"  {PROG} fmt apps/")
    print(f"  {PROG} fmt --check apps/ stdlib/")
    print(f"  {PROG} order hello.ail")
    print(f"  {PROG} order --json apps/")
    print(f"  {PROG} order --fix hello.ail")
    print(f"  {PROG} rename old_name new_name")
    print(f"  {PROG} rename --dry-run old_name new_name")
    print(f"  {PROG} watch")
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

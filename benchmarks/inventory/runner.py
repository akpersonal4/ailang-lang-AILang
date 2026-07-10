"""Inventory benchmark runner — B2 through B6.

Provides CLI entry point for listing, inspecting, and executing inventory
benchmarks against both AILang and Python codebases.
"""

from __future__ import annotations

import json
import sys
import os
import time
import subprocess
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
BENCHMARKS_DIR = HERE.parent
DATASETS_DIR = BENCHMARKS_DIR / "datasets"
PROJECT_ROOT = BENCHMARKS_DIR.parent
APPS_DIR = PROJECT_ROOT / "apps"


def cmd_list() -> int:
    """List all inventory benchmark datasets (B2–B6)."""
    names = sorted(
        d.name for d in DATASETS_DIR.iterdir()
        if d.name.startswith("b") and d.name.endswith("_inventory") and d.is_dir()
    )
    if not names:
        print("No inventory datasets found.")
        print("Expected: b2_inventory, b3_inventory, b4_inventory, b5_inventory, b6_inventory")
        return 1

    print("Inventory Benchmark Datasets")
    print("=" * 50)
    for name in names:
        task_file = DATASETS_DIR / name / "task.json"
        if task_file.is_file():
            try:
                task = json.loads(task_file.read_text(encoding="utf-8"))
                desc = task.get("description", task.get("title", name))
                print(f"  {name}: {desc}")
            except Exception as e:
                print(f"  {name}: error reading task.json — {e}")
        else:
            print(f"  {name}: (no task.json)")
    return 0


def _normalize_benchmark_name(benchmark_id: str) -> str:
    """Normalize benchmark ID to folder name (e.g. 'B2' -> 'b2_inventory')."""
    bid = benchmark_id.lower().removeprefix("b")
    return f"b{bid}_inventory"


def cmd_show(benchmark_id: str, task_id: str | None = None) -> int:
    """Show task definition for a given benchmark."""
    name = _normalize_benchmark_name(benchmark_id)
    dataset_dir = DATASETS_DIR / name
    if not dataset_dir.is_dir():
        print(f"Dataset not found: {dataset_dir}")
        print("Available inventory datasets:")
        cmd_list()
        return 1

    task_file = dataset_dir / "task.json"
    if not task_file.is_file():
        print(f"No task.json in {dataset_dir}")
        return 1

    task = json.loads(task_file.read_text(encoding="utf-8"))

    if task_id:
        tasks = task.get("tasks") or task.get("scenarios") or task.get("bugs") or []
        changes_ref = task.get("changes")
        if isinstance(changes_ref, str) and not tasks:
            changes_path = PROJECT_ROOT / changes_ref
            if not changes_path.is_file():
                changes_path = dataset_dir / changes_ref
            if changes_path.is_file():
                tasks = json.loads(changes_path.read_text(encoding="utf-8"))
        if not isinstance(tasks, list):
            tasks = [tasks]
        found = [t for t in tasks if t.get("id", "").lower() == task_id.lower()]
        if not found:
            print(f"Task '{task_id}' not found in {name}")
            print(f"Available tasks: {[t.get('id') for t in tasks]}")
            return 1
        print(json.dumps(found[0], indent=2))
    else:
        print(json.dumps(task, indent=2))

    return 0


def _get_ail_build_cmd() -> str:
    """Find the `ail` command."""
    for candidate in ["ail", "ail.bat", "ail.exe"]:
        try:
            result = subprocess.run(
                [candidate, "--version"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                return candidate
        except FileNotFoundError:
            continue
    return "ail"


def _build_ailang(files: list[Path]) -> tuple[bool, str]:
    """Build AILang files. Returns (success, output)."""
    ail_cmd = _get_ail_build_cmd()
    build_args = [ail_cmd, "build"] + [str(f) for f in files]
    try:
        result = subprocess.run(
            build_args, capture_output=True, text=True, timeout=120,
        )
        success = result.returncode == 0
        output = result.stdout + result.stderr
        return success, output
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT: build exceeded 120s"
    except FileNotFoundError:
        return False, f"Command not found: {ail_cmd}"


def _run_python_tests(test_script: Path) -> tuple[bool, str]:
    """Run Python test runner. Returns (success, output)."""
    try:
        result = subprocess.run(
            [sys.executable, str(test_script)],
            capture_output=True, text=True, timeout=120,
            cwd=test_script.parent,
        )
        success = result.returncode == 0
        output = result.stdout + result.stderr
        return success, output
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT: python test execution exceeded 120s"


def cmd_run(benchmark_type: str, language: str = "ailang") -> int:
    """Execute an inventory benchmark.

    benchmark_type: B2, B3, B4, B5, or B6
    language: ailang or python
    """
    name = _normalize_benchmark_name(benchmark_type)
    dataset_dir = DATASETS_DIR / name
    if not dataset_dir.is_dir():
        print(f"Dataset not found: {dataset_dir}")
        return 1

    task_file = dataset_dir / "task.json"
    if not task_file.is_file():
        print(f"No task.json in {dataset_dir}")
        return 1

    task = json.loads(task_file.read_text(encoding="utf-8"))
    print(f"Running {name} ({language})")
    print(f"  {task.get('description', task.get('title', ''))}")
    print()

    if language == "ailang":
        source_root = APPS_DIR / "inventory"
        test_root = source_root / "tests"
        test_runner = test_root / "runner.py"
        ail_files = sorted(source_root.rglob("*.ail"))
    else:
        source_root = APPS_DIR / "inventory_py"
        test_root = source_root / "tests"
        test_runner = test_root / "runner.py"
        ail_files = []

    print(f"  Build ({language}): ", end="")
    sys.stdout.flush()
    if language == "ailang":
        build_ok, build_output = _build_ailang(ail_files)
    else:
        build_ok, build_output = True, ""  # Python has no separate build step
    if build_ok:
        print("OK")
    else:
        print("FAIL")
        print(build_output[:2000])

    print(f"  Tests ({language}): ", end="")
    sys.stdout.flush()
    if test_runner.is_file():
        test_ok, test_output = _run_python_tests(test_runner)
    else:
        test_ok, test_output = False, f"Test runner not found: {test_runner}"

    if test_ok:
        print("OK")
    else:
        print("FAIL")
        print(test_output[:2000])

    print()
    if language == "ailang":
        print(f"Source root: {APPS_DIR / 'inventory'}")
    else:
        print(f"Source root: {APPS_DIR / 'inventory_py'}")

    return 0 if (build_ok and test_ok) else 1


def main(argv: list[str] | None = None) -> int:
    """Inventory benchmark CLI entry point."""
    args = argv or sys.argv[2:]  # skip 'inventory'

    if not args:
        print(__doc__)
        return 0

    command = args[0]

    if command == "list":
        return cmd_list()
    elif command == "show" and len(args) >= 2:
        benchmark_id = args[1]
        task_id = args[2] if len(args) >= 3 else None
        return cmd_show(benchmark_id, task_id)
    elif command == "run" and len(args) >= 2:
        benchmark_type = args[1]
        language = args[2] if len(args) >= 3 else "ailang"
        return cmd_run(benchmark_type, language)
    else:
        print(f"Unknown inventory command: {command}")
        print("Usage: python -m benchmarks inventory list|show|run")
        return 1


if __name__ == "__main__":
    sys.exit(main())

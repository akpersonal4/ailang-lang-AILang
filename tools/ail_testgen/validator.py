"""Validation stage — run generated tests to verify correctness."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tools.ail_testgen.models import TestCase
from tools.common.process import run_subprocess


def validate_generated_tests(generated_dir: Path) -> dict:
    """Run all generated test files through pytest and report results.

    Returns a dict with:
      - total: int
      - passed: int
      - failed: list[str] (test names)
      - errors: list[str] (file-level errors)
    """
    py_files = sorted(generated_dir.glob("*.py"))
    total = len(py_files)
    passed = 0
    failed: list[str] = []
    errors: list[str] = []

    for py_file in py_files:
        result = run_subprocess(
            [sys.executable, "-m", "pytest", str(py_file), "--tb=short", "-q"],
            timeout=120,
        )
        if result.exit_code == 0:
            passed += 1
        elif result.exit_code == 1:
            failed.append(py_file.stem)
        else:
            errors.append("%s (exit %d)" % (py_file.stem, result.exit_code))

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
    }

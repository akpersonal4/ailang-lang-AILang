"""Validation stage — run generated tests through ``ail test``."""

from __future__ import annotations

import sys
from pathlib import Path

from tools.common.process import run_subprocess


def validate_generated_tests(generated_dir: Path) -> dict:
    """Run every generated test file through ``ail test`` and report results.

    Returns a dict with:
      - total: int
      - passed: int
      - failed: list[str] (test file stems)
      - errors: list[str] (file-level errors)
    """
    ail_files = sorted(generated_dir.glob("*.ail"))
    total = len(ail_files)
    passed = 0
    failed: list[str] = []
    errors: list[str] = []

    for ail_file in ail_files:
        # Run ``ail test`` against the individual file so each generated
        # test is validated in isolation. ``ail test`` returns exit 0 for
        # PASS, 1 for FAIL, and other codes for hard errors.
        result = run_subprocess(
            [sys.executable, "-m", "compiler.cli.main", "test", "--no-check",
             str(ail_file)],
            timeout=120,
        )
        if result.exit_code == 0:
            passed += 1
        elif result.exit_code == 1:
            failed.append(ail_file.stem)
        else:
            errors.append(f"{ail_file.stem} (exit {result.exit_code})")

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
    }

"""Shared process execution utilities for DX tools."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass


@dataclass
class ProcessResult:
    stdout: str
    stderr: str
    exit_code: int


def run_subprocess(
    args: list[str],
    timeout: int | None = None,
    cwd: str | None = None,
) -> ProcessResult:
    """Run a subprocess and return captured output.

    Args:
        args: Command and arguments to execute.
        timeout: Maximum wall-clock time in seconds. Default: no timeout.
        cwd: Working directory for the subprocess.

    Returns:
        ProcessResult with stdout, stderr, and exit_code.

    Raises:
        subprocess.TimeoutExpired: If the subprocess exceeds the timeout.
    """
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
        return ProcessResult(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
        )
    except subprocess.TimeoutExpired:
        return ProcessResult(
            stdout="",
            stderr=f"TIMEOUT after {timeout}s",
            exit_code=-1,
        )


def run_ail_build(filepath: str, timeout: int = 120) -> ProcessResult:
    """Run ail build on a file and return the result."""
    return run_subprocess([sys.executable, "-m", "compiler", "build", filepath], timeout=timeout)


def run_ail_run(filepath: str, timeout: int = 120, args: list[str] | None = None) -> ProcessResult:
    """Run ail run on a file and return the result."""
    cmd = [sys.executable, "-m", "compiler", "run", filepath]
    if args:
        cmd.extend(args)
    return run_subprocess(cmd, timeout=timeout)

"""Regression tests for `ail benchmark` progress streaming (M136 J-3).

The benchmark command previously emitted zero output while stdout was a
pipe: all progress ``print()`` calls were block-buffered, so a long suite
(such as the canonical suite, dominated by the static_analyzer app at
~30-85s per run) looked like a hang even though it eventually completed.
These tests lock in the fix: progress lines must be flushed as they are
written.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from tools.ail_benchmark.discovery import Benchmark, benchmark_apps_dir
from tools.ail_benchmark.runner import run_benchmark

REPO_ROOT = Path(__file__).resolve().parents[1]


class _FlushTrackingWriter:
    """Minimal stdout stand-in that records write() and flush() calls."""

    def __init__(self) -> None:
        self.buffer = ""
        self.flushes = 0

    def write(self, text: str) -> int:
        self.buffer += text
        return len(text)

    def flush(self) -> None:
        self.flushes += 1


def _dice_roller_benchmark() -> Benchmark:
    apps_dir = benchmark_apps_dir(REPO_ROOT)
    path = apps_dir / "dice_roller" / "main.ail"
    assert path.is_file(), f"Missing benchmark app at {path}"
    return Benchmark(name="dice_roller", path=path, suite="test")


class TestBenchmarkProgressStreaming:
    def test_progress_lines_are_flushed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Progress output must be explicitly flushed (not block-buffered)."""
        writer = _FlushTrackingWriter()
        monkeypatch.setattr(sys, "stdout", writer)
        monkeypatch.setenv("PYTHONPATH", str(REPO_ROOT))

        result = run_benchmark(_dice_roller_benchmark(), repeat=1, quiet=False)

        assert result.status == "pass"
        assert "Building dice_roller..." in writer.buffer
        assert "Running dice_roller..." in writer.buffer
        assert "[OK] dice_roller" in writer.buffer
        assert writer.flushes >= 1, (
            "progress lines were not flushed; benchmark output stays "
            "block-buffered when stdout is a pipe (J-3 hang symptom)"
        )

    def test_benchmark_command_streams_and_succeeds(self, tmp_path: Path) -> None:
        """End-to-end: `ail benchmark --app` exits 0 and writes its report."""
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT)
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.ail_benchmark",
                "--app",
                "dice_roller",
                "--repeat",
                "1",
            ],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert proc.returncode == 0, (
            f"benchmark exited {proc.returncode}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
        assert "AILang Benchmark Runner" in proc.stdout
        assert ">> dice_roller" in proc.stdout
        assert "[elapsed" in proc.stdout
        report = tmp_path / "generated" / "benchmarks" / "BENCHMARK_REPORT.json"
        assert report.is_file(), f"Expected report at {report}"

"""Calibration execution — validates measurement infrastructure.

Runs identical prompts across all configured providers and verifies
that the measurement framework produces consistent, correct results.

This is NOT a provider comparison. No conclusions about provider quality
should be drawn from calibration output.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from benchmarks.framework.environment import snapshot
from benchmarks.framework.reporting import generate_run_id
from benchmarks.providers import AIProvider, ProviderResult, create_provider

# ── Calibration Prompts ───────────────────────────────────────────────

CALIBRATION_PROMPTS: list[dict[str, str]] = [
    {
        "name": "short_response",
        "prompt": "Hello. Respond with exactly: Calibration OK",
    },
    {
        "name": "code_understanding",
        "prompt": (
            "Read this code and explain what it does in one sentence:\n\n"
            "fn add(a, b) { return a + b; }\n"
            "fn main() { return add(3, 4); }\n"
        ),
    },
    {
        "name": "token_counting",
        "prompt": ("Count to 5. Respond with exactly: 1 2 3 4 5"),
    },
]


# ── Calibration Result ────────────────────────────────────────────────


@dataclass
class CalibrationRun:
    """Result from a single calibration prompt against one provider."""

    prompt_name: str
    provider_name: str
    model: str
    result: ProviderResult
    run_id: str = ""
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt_name": self.prompt_name,
            "provider_name": self.provider_name,
            "model": self.model,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "result": self.result.to_dict(),
        }


@dataclass
class CalibrationReport:
    """Complete calibration report for one execution."""

    calibration_version: str
    run_id: str
    timestamp: str
    environment: dict[str, Any]
    runs: list[CalibrationRun] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "calibration_version": self.calibration_version,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "environment": self.environment,
            "runs": [r.to_dict() for r in self.runs],
            "errors": self.errors,
        }


CALIBRATION_VERSION = "0.1.0"


# ── Main Calibration Logic ────────────────────────────────────────────


def _load_providers(config_path: str | None = None) -> list[AIProvider]:
    """Load providers from configuration or environment.

    Configuration file format (JSON):
    {
        "providers": [
            {"name": "openai", "model": "gpt-4o"},
            {"name": "anthropic", "model": "claude-3-5-sonnet-20241022"},
            {"name": "local", "model": "llama3.2", "base_url": "http://localhost:11434/v1"}
        ]
    }

    If no config file is given, attempt to load from environment variables.
    Only providers with available API keys are loaded.
    """
    import os

    providers: list[AIProvider] = []

    if config_path:
        path = Path(config_path)
        if not path.exists():
            print(f"  [WARN] Config file not found: {config_path}")
            return providers
        try:
            config = json.loads(path.read_text(encoding="utf-8"))
            for entry in config.get("providers", []):
                name = entry.get("name", "")
                model = entry.get("model", "")
                kwargs = {k: v for k, v in entry.items() if k not in ("name", "model")}
                try:
                    provider = create_provider(name, model=model, **kwargs)
                    providers.append(provider)
                except (ValueError, ImportError) as e:
                    print(f"  [SKIP] {name}: {e}")
        except Exception as e:
            print(f"  [ERROR] Failed to load config: {e}")
        return providers

    # Auto-detect from environment
    auto_configs = [
        ("openai", "gpt-4o", "OPENAI_API_KEY"),
        ("anthropic", "claude-3-5-sonnet-20241022", "ANTHROPIC_API_KEY"),
        ("google", "gemini-2.0-flash", "GOOGLE_API_KEY"),
    ]
    for name, default_model, env_var in auto_configs:
        if os.environ.get(env_var):
            try:
                provider = create_provider(name, model=default_model)
                providers.append(provider)
            except (ValueError, ImportError) as e:
                print(f"  [SKIP] {name}: {e}")

    # Always try local (no key required)
    try:
        provider = create_provider("local")
        providers.append(provider)
    except (ValueError, ImportError) as e:
        print(f"  [SKIP] local: {e}")

    return providers


def _identity(x): ...
def run_calibration(
    providers: list[AIProvider] | None = None,
    config_path: str | None = None,
    output_dir: str | None = None,
    quiet: bool = False,
) -> CalibrationReport:
    """Execute calibration against all providers.

    Args:
        providers: Optional list of providers. If None, auto-detect.
        config_path: Optional path to provider config JSON.
        output_dir: Optional output directory for calibration report.

    Returns:
        CalibrationReport with all measurements.
    """
    if providers is None:
        providers = _load_providers(config_path)

    env = snapshot()
    run_id = generate_run_id()
    report = CalibrationReport(
        calibration_version=CALIBRATION_VERSION,
        run_id=run_id,
        timestamp=env["timestamp"],
        environment=env,
    )

    if not providers:
        report.errors.append("No providers available for calibration")
        if not quiet:
            print("No providers available for calibration.")
            print("Set API keys or provide a config file.")
        return report

    if not quiet:
        print(f"AILang AI Provider Calibration v{CALIBRATION_VERSION}")
        print(f"Run ID: {run_id}")
        print(f"Providers: {len(providers)}")
        for p in providers:
            print(f"  - {p.provider_name}: {p.model}")
        print()

    for provider in providers:
        for prompt_def in CALIBRATION_PROMPTS:
            name = prompt_def["name"]
            prompt_text = prompt_def["prompt"]

            if not quiet:
                print(f"  [{provider.provider_name}] {name}... ", end="", flush=True)

            try:
                result = provider.complete(prompt_text)

                cal_run = CalibrationRun(
                    prompt_name=name,
                    provider_name=provider.provider_name,
                    model=provider.model,
                    result=result,
                    run_id=run_id,
                    timestamp=result.timestamp,
                )
                report.runs.append(cal_run)

                if not quiet:
                    status = result.completion_status
                    latency = result.request_latency_seconds
                    tokens = result.response_tokens or "?"
                    print(f"{status} ({latency:.2f}s, {tokens} resp. tokens)")

            except Exception as e:
                error_result = ProviderResult(
                    provider_name=provider.provider_name,
                    model=provider.model,
                    timestamp=datetime.now(UTC).isoformat(),
                    completion_status="error",
                    failure_reason=str(e),
                )
                report.runs.append(
                    CalibrationRun(
                        prompt_name=name,
                        provider_name=provider.provider_name,
                        model=provider.model,
                        result=error_result,
                        run_id=run_id,
                        timestamp=error_result.timestamp,
                    )
                )
                report.errors.append(f"[{provider.provider_name}] {name}: {e}")
                if not quiet:
                    print(f"ERROR: {e}")

    # Write report
    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        report_file = out_path / f"calibration_{run_id}.json"
        report_file.write_text(
            json.dumps(report.to_dict(), indent=2, default=str),
            encoding="utf-8",
        )
        if not quiet:
            print(f"\nCalibration report: {report_file}")

    return report


# ── CLI entry point ───────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    """Run calibration from command line.

    Usage:
        python -m benchmarks.calibration.run
        python -m benchmarks.calibration.run --config providers.json
        python -m benchmarks.calibration.run --output results/
    """
    import argparse

    parser = argparse.ArgumentParser(description="AILang AI Provider Calibration")
    parser.add_argument(
        "--config",
        "-c",
        help="Path to provider configuration JSON",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output directory for calibration report",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress output",
    )

    args = parser.parse_args(argv)

    report = run_calibration(
        config_path=args.config,
        output_dir=args.output,
        quiet=args.quiet,
    )

    if report.errors:
        if not args.quiet:
            print(f"\nCalibration completed with {len(report.errors)} error(s):")
            for err in report.errors:
                print(f"  - {err}")
        return 1

    if not report.runs:
        if not args.quiet:
            print("\nNo calibration runs executed.")
        return 1

    if not args.quiet:
        print(
            f"\nCalibration complete: {len(report.runs)} runs, "
            f"{len(report.errors)} errors."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

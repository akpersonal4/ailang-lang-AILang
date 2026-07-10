"""AILang Engineering Benchmark Program — CLI entry point.

Usage:
    python -m benchmarks setup            # Initialize datasets
    python -m benchmarks b1               # Run B1 benchmark
    python -m benchmarks calibrate        # Run AI provider calibration
    python -m benchmarks inventory list   # List inventory benchmark datasets
    python -m benchmarks inventory show B2  # Show B2 task definition
    python -m benchmarks inventory run B2 ailang  # Run B2 against AILang
    python -m benchmarks list             # List registered datasets
    python -m benchmarks list-providers   # List registered AI providers
    python -m benchmarks test             # Run framework acceptance tests
"""

from __future__ import annotations

import sys
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent


def cmd_setup() -> int:
    """Initialize benchmark datasets."""
    from benchmarks.setup import main
    return main()


def cmd_b1() -> int:
    """Run B1 — AI Repository Understanding Benchmark."""
    from benchmarks.b1_understanding.run import main
    return main()


def cmd_calibrate() -> int:
    """Run AI provider calibration."""
    from benchmarks.calibration.run import main
    return main(sys.argv[2:])


def cmd_list() -> int:
    """List registered datasets and their metadata."""
    datasets_dir = HERE / "datasets"

    if not datasets_dir.is_dir():
        print("No datasets directory. Run: python -m benchmarks setup")
        return 1

    import json
    dataset_names = sorted(
        d.name for d in datasets_dir.iterdir()
        if d.is_dir() and (d / "metadata.json").exists()
    )

    if not dataset_names:
        print("No datasets found. Run: python -m benchmarks setup")
        return 1

    print("Registered Benchmark Datasets")
    print("=" * 50)
    for name in dataset_names:
        meta_path = datasets_dir / name / "metadata.json"
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            print(f"  {name}:")
            print(f"    LOC: {meta.get('loc', '?')}")
            print(f"    Files: {meta.get('file_count', '?')}")
            print(f"    Modules: {meta.get('module_count', '?')}")
            print(f"    Symbols: {meta.get('symbol_count', '?')}")
            print(f"    Dependencies: {meta.get('dependency_count', '?')}")
            print(f"    Doc: {meta.get('doc_size_bytes', '?')} bytes")
        except Exception as e:
            print(f"  {name}: error reading metadata — {e}")
    return 0


def cmd_list_providers() -> int:
    """List registered AI providers."""
    from benchmarks.providers import list_providers, PROVIDER_REGISTRY

    names = list_providers()
    print("Registered AI Providers")
    print("=" * 50)
    for name in names:
        cls = PROVIDER_REGISTRY.get(name)
        doc = (cls.__doc__ or "").strip().split("\n")[0] if cls else ""
        env_var = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
            "local": "(no key required)",
        }.get(name, "")
        print(f"  {name}: {doc}")
        print(f"    Env: {env_var}")
    return 0


def cmd_test() -> int:
    """Run framework acceptance and regression tests."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(HERE / "tests"), "-v"],
        capture_output=False,
    )
    return result.returncode


def cmd_inventory() -> int:
    """Run inventory management system benchmarks (B2–B6)."""
    from benchmarks.inventory.runner import main
    return main()


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 0

    command = sys.argv[1]
    commands = {
        "setup": cmd_setup,
        "b1": cmd_b1,
        "calibrate": cmd_calibrate,
        "inventory": cmd_inventory,
        "list": cmd_list,
        "list-providers": cmd_list_providers,
        "test": cmd_test,
    }

    cmd = commands.get(command)
    if cmd is None:
        print(f"Unknown command: {command}")
        print(__doc__)
        return 1

    return cmd()


if __name__ == "__main__":
    sys.exit(main())

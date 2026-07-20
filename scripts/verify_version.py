#!/usr/bin/env python3
"""Verify version consistency across all sources."""

import subprocess
import sys
import tomllib
from pathlib import Path


def main():
    # Find repo root
    repo_root = Path(__file__).parent.parent

    # Read pyproject.toml version
    with open(repo_root / "pyproject.toml", "rb") as f:
        pyproject_version = tomllib.load(f)["project"]["version"]

    # Check compiler.__version__
    sys.path.insert(0, str(repo_root))
    import compiler

    module_version = compiler.__version__

    # Check CLI version
    result = subprocess.run(["ail", "--version"], capture_output=True, text=True)
    cli_version = result.stdout.strip().replace("AILang v", "")

    # Check python -m compiler --version
    result = subprocess.run(
        [sys.executable, "-m", "compiler", "--version"], capture_output=True, text=True
    )
    module_cli_version = result.stdout.strip().replace("AILang v", "")

    # Verify all match
    all_versions = [pyproject_version, module_version, cli_version, module_cli_version]
    if len(set(all_versions)) != 1:
        print("ERROR: Version mismatch detected!")
        print(f"  pyproject.toml: {pyproject_version}")
        print(f"  compiler.__version__: {module_version}")
        print(f"  ail --version: {cli_version}")
        print(f"  python -m compiler --version: {module_cli_version}")
        return 1

    print(f"All version sources consistent: {pyproject_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

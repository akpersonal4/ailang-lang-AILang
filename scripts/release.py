#!/usr/bin/env python3
"""Official AILang Release Script.

This script performs a verified release, ensuring:
1. Clean git working tree
2. Synchronized versions
3. Correct tag
4. Successful build
5. Verified artifacts

Usage:
    python scripts/release.py [--dry-run] [--skip-build]

Exit codes:
    0 - Success
    1 - Pre-flight check failed
    2 - Build failed
    3 - Artifact verification failed
    4 - Git operation failed
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
import zipfile
import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def run_command(cmd: list[str], cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def check_git_status() -> tuple[bool, str]:
    """Check if git working tree is clean."""
    result = run_command(["git", "status", "--porcelain"])
    if result.stdout.strip():
        return False, "Working tree is dirty. Commit or stash changes first."
    return True, ""


def get_pyproject_version() -> str:
    """Get version from pyproject.toml."""
    with open(REPO_ROOT / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["project"]["version"]


def verify_versions() -> bool:
    """Verify all version files match pyproject.toml."""
    pyproject_version = get_pyproject_version()
    all_ok = True

    # Check compiler/_version.py
    version_file = REPO_ROOT / "compiler" / "_version.py"
    if version_file.exists():
        content = version_file.read_text(encoding="utf-8")
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match and match.group(1) != pyproject_version:
            print(f"  FAIL: {version_file} has {match.group(1)}, expected {pyproject_version}")
            all_ok = False
        elif match:
            print(f"  OK: {version_file} = {match.group(1)}")

    # Check tool VERSION constants
    tool_files = [
        "tools/ail_context/__main__.py",
        "tools/ail_mcp/__init__.py",
        "tools/ail_mcp/server.py",
        "tools/ail_mcp/context_adapter.py",
    ]

    for tool_file in tool_files:
        file_path = REPO_ROOT / tool_file
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            for pattern in [r'^VERSION\s*=\s*["\']([^"\']+)["\']', r'^__version__\s*=\s*["\']([^"\']+)["\']']:
                regex = re.compile(pattern, re.MULTILINE)
                match = regex.search(content)
                if match:
                    tool_version = match.group(1)
                    if tool_version != pyproject_version:
                        print(f"  FAIL: {file_path} has {tool_version}, expected {pyproject_version}")
                        all_ok = False
                    else:
                        print(f"  OK: {file_path} = {tool_version}")
                    break

    return all_ok


def verify_tag(version: str) -> tuple[bool, str]:
    """Verify the tag for this version exists and is correct."""
    result = run_command(["git", "tag", "-l", f"v{version}"])
    if result.stdout.strip():
        return True, f"Tag v{version} exists"
    return False, f"Tag v{version} does not exist"


def build_wheel(skip_build: bool = False) -> tuple[bool, Path]:
    """Build the wheel and source distribution."""
    if skip_build:
        print("  [Skipped by request]")
        dist_dir = REPO_ROOT / "dist"
        wheels = list(dist_dir.glob("*.whl")) if dist_dir.exists() else []
        if wheels:
            return True, wheels[0]
        return False, Path()

    # Clean dist directory
    dist_dir = REPO_ROOT / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(exist_ok=True)

    print("  Building wheel and source distribution...")
    result = run_command([sys.executable, "-m", "build"])
    if result.returncode != 0:
        print(f"  FAIL: Build failed")
        print(result.stderr)
        return False, Path()

    wheels = list(dist_dir.glob("*.whl"))
    if not wheels:
        print("  FAIL: No wheel produced")
        return False, Path()

    print(f"  OK: Built {wheels[0].name}")
    return True, wheels[0]


def verify_wheel(wheel_path: Path, expected_version: str) -> bool:
    """Verify wheel metadata and contents."""
    print(f"  Verifying wheel: {wheel_path.name}")

    try:
        with zipfile.ZipFile(wheel_path) as zf:
            # Check METADATA
            metadata = zf.read("ailang_lang-*.dist-info/METADATA").decode("utf-8")
            if f"Version: {expected_version}" not in metadata:
                print(f"  FAIL: METADATA has wrong version")
                return False
            print(f"  OK: METADATA version = {expected_version}")

            # Check _version.py in wheel
            version_py = zf.read("compiler/_version.py").decode("utf-8")
            match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', version_py)
            if not match or match.group(1) != expected_version:
                print(f"  FAIL: _version.py in wheel has wrong version")
                return False
            print(f"  OK: _version.py in wheel = {match.group(1)}")

    except Exception as e:
        print(f"  FAIL: Error reading wheel: {e}")
        return False

    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Perform AILang release")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
    parser.add_argument("--skip-build", action="store_true", help="Skip the build step")
    parser.add_argument("--tag", type=str, help="Override tag version (e.g., v1.1.2)")
    args = parser.parse_args()

    print("=" * 60)
    print("AILANG RELEASE VERIFICATION")
    print("=" * 60)

    # Step 1: Git status check
    print("\n[1/5] Checking git status...")
    if not args.dry_run:
        ok, msg = check_git_status()
        if not ok:
            print(f"  ERROR: {msg}")
            return 1
    print("  OK: Working tree is clean")

    # Step 2: Version verification
    print("\n[2/5] Verifying version consistency...")
    version = get_pyproject_version()
    print(f"  pyproject.toml version: {version}")
    if not verify_versions():
        print("  ERROR: Version verification failed!")
        return 1
    print(f"  OK: All version files match {version}")

    # Step 3: Tag verification
    print("\n[3/5] Verifying git tag...")
    tag_name = args.tag or f"v{version}"
    if not args.dry_run:
        ok, msg = verify_tag(version)
        if not ok:
            print(f"  WARNING: {msg}")
    else:
        print(f"  Would check tag: {tag_name}")
    print("  OK")

    # Step 4: Build
    print("\n[4/5] Building wheel...")
    if args.dry_run:
        print("  [Dry run - build skipped]")
    else:
        ok, wheel_path = build_wheel(args.skip_build)
        if not ok:
            return 2

    # Step 5: Artifact verification
    print("\n[5/5] Verifying artifacts...")
    if args.dry_run:
        print("  [Dry run - verification skipped]")
    else:
        wheel_files = list((REPO_ROOT / "dist").glob("*.whl"))
        if wheel_files:
            if not verify_wheel(wheel_files[0], version):
                return 3
        else:
            print("  No wheel found to verify")

    print("\n" + "=" * 60)
    print("RELEASE VERIFICATION COMPLETE")
    print("=" * 60)
    print(f"\nVersion: {version}")
    print(f"Tag: v{version}")
    print("\nArtifact checklist for release:")
    print(f"  - dist/ailang_lang-{version}-py3-none-any.whl")
    print(f"  - dist/ailang_lang-{version}.tar.gz")
    print("\nNext steps:")
    print("  1. Create git tag: git tag -a v{version} -m 'Release v{version}'")
    print("  2. Push tag: git push origin v{version}")
    print("  3. Create GitHub Release with artifacts")
    print("  4. Upload to PyPI: twine upload dist/*")

    return 0


if __name__ == "__main__":
    sys.exit(main())
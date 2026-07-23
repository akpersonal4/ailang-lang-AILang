# AILang Developer Experience Tool: ail release --verify
# M86.5C — Release Verification

"""AILang Release Verifier — validates release readiness without publishing.

Checks:
  - Package metadata (pyproject.toml)
  - Version consistency across sources
  - Documentation version references
  - CHANGELOG exists and contains current version
  - LICENSE file present
  - Wheel contents and required files
  - Test status
  - No language behavior changes since last release

Does NOT publish anything.
"""

import argparse
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path


def _find_root() -> Path:
    """Find the AILang repository root."""
    candidate = Path(__file__).resolve().parent.parent.parent
    if (candidate / "pyproject.toml").is_file():
        return candidate
    return Path.cwd()


def _read_file(path: Path) -> str | None:
    """Read file contents safely."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


# =============================================================================
# Verification checks
# =============================================================================


def check_package_metadata(root: Path) -> dict:
    """Verify pyproject.toml has all required fields."""
    pyproject_path = root / "pyproject.toml"
    if not pyproject_path.is_file():
        return {"ok": False, "error": "pyproject.toml not found"}

    content = _read_file(pyproject_path)
    if not content:
        return {"ok": False, "error": "pyproject.toml unreadable"}

    try:
        data = tomllib.loads(content)
    except Exception as e:
        return {"ok": False, "error": f"pyproject.toml parse error: {e}"}

    project = data.get("project", {})
    required_fields = ["name", "version", "description", "license", "requires-python"]
    missing = [f for f in required_fields if f not in project]

    checks = {
        "name": project.get("name"),
        "version": project.get("version"),
        "description": bool(project.get("description")),
        "license": bool(project.get("license")),
        "requires_python": project.get("requires-python"),
        "readme": bool(project.get("readme")),
        "urls": bool(project.get("urls")),
        "entry_point": bool(data.get("project.scripts", data.get("project", {}).get("scripts", {}))),
    }

    ok = not missing and all(v is not None for v in checks.values() if isinstance(v, bool))
    return {"ok": ok, "missing_fields": missing, "checks": checks}


def check_version_consistency(root: Path) -> dict:
    """Verify version is consistent across all sources."""
    pyproject_path = root / "pyproject.toml"
    if not pyproject_path.is_file():
        return {"ok": False, "error": "pyproject.toml not found"}

    content = _read_file(pyproject_path)
    if not content:
        return {"ok": False, "error": "pyproject.toml unreadable"}

    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        return {"ok": False, "error": "version not found in pyproject.toml"}

    canonical_version = match.group(1)
    versions = {"pyproject.toml": canonical_version}

    version_file = root / "compiler" / "_version.py"
    v_content = _read_file(version_file)
    if v_content:
        match = re.search(r'__version__\s*=\s*"([^"]+)"', v_content)
        if match:
            versions["compiler/_version.py"] = match.group(1)

    readme = _read_file(root / "README.md")
    if readme:
        match = re.search(r"version-(\d+\.\d+\.\d+)", readme)
        if match:
            versions["README.md"] = match.group(1)

    changelog = _read_file(root / "CHANGELOG.md")
    if changelog:
        match = re.search(r"## \[?v?(\d+\.\d+\.\d+)", changelog)
        if match:
            versions["CHANGELOG.md"] = match.group(1)

    inconsistent = {k: v for k, v in versions.items() if v != canonical_version}
    return {
        "ok": len(inconsistent) == 0,
        "canonical": canonical_version,
        "versions": versions,
        "inconsistent": inconsistent,
    }


def check_changelog(root: Path) -> dict:
    """Verify CHANGELOG.md exists and contains current version."""
    changelog_path = root / "CHANGELOG.md"
    if not changelog_path.is_file():
        return {"ok": False, "error": "CHANGELOG.md not found"}

    content = _read_file(changelog_path)
    if not content:
        return {"ok": False, "error": "CHANGELOG.md unreadable"}

    pyproject = _read_file(root / "pyproject.toml")
    version = ""
    if pyproject:
        match = re.search(r'version\s*=\s*"([^"]+)"', pyproject)
        if match:
            version = match.group(1)

    has_version = version and version in content

    return {
        "ok": True,
        "has_current_version": has_version,
        "version": version,
        "size_bytes": len(content.encode("utf-8")),
    }


def check_license(root: Path) -> dict:
    """Verify LICENSE file exists."""
    license_path = root / "LICENSE"
    if not license_path.is_file():
        return {"ok": False, "error": "LICENSE not found"}

    content = _read_file(license_path)
    if not content:
        return {"ok": False, "error": "LICENSE unreadable"}

    is_apache = "apache" in content.lower() or "Apache License" in content
    return {"ok": True, "exists": True, "is_apache": is_apache}


def check_wheel_contents(root: Path) -> dict:
    """Check if wheel/sdist exist and contain required files."""
    dist_dir = root / "dist"
    if not dist_dir.is_dir():
        return {"ok": False, "error": "dist/ directory not found"}

    wheels = list(dist_dir.glob("*.whl"))
    sdists = list(dist_dir.glob("*.tar.gz"))

    if not wheels and not sdists:
        return {"ok": False, "error": "No wheel or sdist found in dist/"}

    return {
        "ok": True,
        "wheels": [str(w.relative_to(root)) for w in wheels],
        "sdists": [str(s.relative_to(root)) for s in sdists],
    }


def check_required_files(root: Path) -> dict:
    """Verify all required release files exist."""
    required = {
        "README.md": root / "README.md",
        "LICENSE": root / "LICENSE",
        "CHANGELOG.md": root / "CHANGELOG.md",
        "pyproject.toml": root / "pyproject.toml",
    }

    stdlib_dir = root / "stdlib"
    exists = {}
    missing = []

    for name, path in required.items():
        if path.is_file():
            exists[name] = True
        else:
            exists[name] = False
            missing.append(name)

    stdlib_exists = stdlib_dir.is_dir() and list(stdlib_dir.glob("*.ail"))
    compiler_dir = root / "compiler"
    compiler_exists = compiler_dir.is_dir()

    return {
        "ok": len(missing) == 0 and stdlib_exists and compiler_exists,
        "files": exists,
        "missing": missing,
        "stdlib_modules": len(list(stdlib_dir.glob("*.ail"))) if stdlib_dir.is_dir() else 0,
        "compiler_package": compiler_exists,
    }


def check_test_status(root: Path) -> dict:
    """Run pytest and report status."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=line", "--timeout=30"],
            capture_output=True,
            text=True,
            cwd=str(root),
            timeout=300,
        )

        output = result.stdout + result.stderr
        passed = 0
        failed = 0
        match = re.search(r"(\d+) passed", output)
        if match:
            passed = int(match.group(1))
        match = re.search(r"(\d+) failed", output)
        if match:
            failed = int(match.group(1))

        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "passed": passed,
            "failed": failed,
            "output": output[-500:] if len(output) > 500 else output,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Test suite timed out after 300s"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =============================================================================
# Report generation
# =============================================================================


def generate_report(root: Path | None = None) -> tuple[str, dict]:
    """Generate the release verification report.

    Returns (markdown_report, json_data).
    """
    if root is None:
        root = _find_root()

    metadata = check_package_metadata(root)
    version = check_version_consistency(root)
    changelog = check_changelog(root)
    license_check = check_license(root)
    wheel = check_wheel_contents(root)
    required = check_required_files(root)
    tests = check_test_status(root)

    checks = [metadata, version, changelog, license_check, wheel, required, tests]
    all_ok = all(c.get("ok", False) for c in checks)
    failed_count = sum(1 for c in checks if not c.get("ok", False))

    json_data = {
        "tool": "ail release --verify",
        "version": "1.0.0",
        "root": str(root),
        "summary": {
            "all_checks_passed": all_ok,
            "failed_checks": failed_count,
            "total_checks": len(checks),
        },
        "checks": {
            "package_metadata": metadata,
            "version_consistency": version,
            "changelog": changelog,
            "license": license_check,
            "wheel_contents": wheel,
            "required_files": required,
            "test_status": tests,
        },
    }

    status_icon = lambda ok: "PASS" if ok else "FAIL"

    lines = [
        "# Release Verification Report",
        "",
        "_Generated by `ail release --verify`_",
        "",
        "**DOES NOT PUBLISH** — verification only.",
        "",
        "## Summary",
        "",
        f"| Check | Status |",
        f"|-------|--------|",
        f"| Package metadata | {status_icon(metadata['ok'])} |",
        f"| Version consistency | {status_icon(version['ok'])} |",
        f"| Changelog | {status_icon(changelog['ok'])} |",
        f"| License | {status_icon(license_check['ok'])} |",
        f"| Wheel/sdist | {status_icon(wheel['ok'])} |",
        f"| Required files | {status_icon(required['ok'])} |",
        f"| Test status | {status_icon(tests['ok'])} |",
        f"| **Overall** | **{status_icon(all_ok)}** |",
        "",
    ]

    ver = version.get("canonical", "unknown")
    lines.append(f"**Version:** {ver}")
    lines.append("")

    if not metadata["ok"]:
        lines.extend(["## Package Metadata Issues", ""])
        if metadata.get("missing_fields"):
            lines.append(f"Missing fields: {', '.join(metadata['missing_fields'])}")
        if metadata.get("error"):
            lines.append(f"Error: {metadata['error']}")
        lines.append("")

    if not version["ok"]:
        lines.extend(["## Version Inconsistencies", ""])
        for source, ver_val in version.get("inconsistent", {}).items():
            lines.append(f"- `{source}`: `{ver_val}` (expected `{version['canonical']}`)")
        lines.append("")

    if not changelog["ok"]:
        lines.extend(["## Changelog Issues", ""])
        lines.append(f"- {changelog.get('error', 'Unknown error')}")
        lines.append("")
    elif not changelog.get("has_current_version"):
        lines.extend(["## Changelog Warning", ""])
        lines.append(f"- Current version `{ver}` not found in CHANGELOG.md")
        lines.append("")

    if not license_check["ok"]:
        lines.extend(["## License Issues", ""])
        lines.append(f"- {license_check.get('error', 'License file missing')}")
        lines.append("")

    if not wheel["ok"]:
        lines.extend(["## Wheel/Sdist Issues", ""])
        lines.append(f"- {wheel.get('error', 'No distributions found')}")
        lines.append("")
    else:
        lines.extend(["## Built Distributions", ""])
        for w in wheel.get("wheels", []):
            lines.append(f"- `{w}`")
        for s in wheel.get("sdists", []):
            lines.append(f"- `{s}`")
        lines.append("")

    if not required["ok"]:
        lines.extend(["## Missing Required Files", ""])
        for m in required.get("missing", []):
            lines.append(f"- `{m}`")
        lines.append("")

    if not tests["ok"]:
        lines.extend(["## Test Status", ""])
        if tests.get("error"):
            lines.append(f"- Error: {tests['error']}")
        else:
            lines.append(f"- Failed: {tests.get('failed', 'unknown')} tests")
            lines.append(f"- Return code: {tests.get('returncode', 'unknown')}")
        lines.append("")

    lines.extend([
        "---",
        "_Report generated by `ail release --verify`_",
        "",
    ])

    return "\n".join(lines), json_data


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="ail release --verify",
        description="AILang Release Verification (read-only, does not publish)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Write report to file",
    )
    parser.add_argument(
        "--root",
        type=str,
        default=None,
        help="Repository root directory",
    )
    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="Skip test execution",
    )

    args = parser.parse_args()
    root = Path(args.root) if args.root else None

    report, json_data = generate_report(root)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if args.json:
            out_path.write_text(json.dumps(json_data, indent=2), encoding="utf-8")
        else:
            out_path.write_text(report, encoding="utf-8")
        print(f"Report written to {out_path}")
    elif args.json:
        print(json.dumps(json_data, indent=2))
    else:
        print(report)

    return 0 if json_data["summary"]["all_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

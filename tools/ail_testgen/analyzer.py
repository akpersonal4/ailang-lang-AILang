"""Analysis stage — coverage analysis and gap detection."""

from __future__ import annotations

from pathlib import Path

from tools.ail_testgen.models import AppInfo, TestCase, TestCategory, CoverageReport


def analyze_coverage(
    apps: list[AppInfo],
    existing_tests: list[Path],
) -> CoverageReport:
    """Determine which apps already have test coverage."""
    tested_names = _find_tested_app_names(existing_tests)
    untested = [a.name for a in apps if a.name not in tested_names]
    total = len(apps)
    tested = len(set(tested_names) & {a.name for a in apps})
    pct = (tested / total * 100) if total > 0 else 0.0
    return CoverageReport(
        apps_total=total,
        apps_with_tests=tested,
        apps_without_tests=len(untested),
        untested_apps=untested,
        coverage_pct=round(pct, 1),
    )


def find_missing_tests(
    apps: list[AppInfo],
    existing_tests: list[Path],
) -> list[TestCase]:
    """Generate TestCase objects for apps missing test coverage."""
    tested_names = _find_tested_app_names(existing_tests)
    missing = [a for a in apps if a.name not in tested_names]
    cases: list[TestCase] = []
    for app in missing:
        cases.append(TestCase(
            app_name=app.name,
            source_file=app.source_file,
            category=TestCategory.BUILD,
            test_name="test_build",
            description="Verify the file compiles successfully.",
        ))
        cases.append(TestCase(
            app_name=app.name,
            source_file=app.source_file,
            category=TestCategory.RUN,
            test_name="test_run",
            description="Verify the file runs with default arguments.",
        ))
    return cases


def _find_tested_app_names(existing_tests: list[Path]) -> set[str]:
    """Extract app names from existing test file names."""
    names: set[str] = set()
    for path in existing_tests:
        stem = path.stem
        if stem.startswith("test_app_"):
            names.add(stem[len("test_app_"):])
        elif stem.startswith("test_"):
            name = stem[len("test_"):]
            name = name.replace("_generated", "")
            names.add(name)
    return names

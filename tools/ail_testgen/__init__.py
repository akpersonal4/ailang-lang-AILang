"""AILang Test Generator — DX-005.

Auto-discovers AILang apps, analyzes coverage gaps, and generates
pytest-compatible test files in tests/generated/.

Processing pipeline:
  Discovery → Analysis → Generation
"""

from tools.ail_testgen.analyzer import analyze_coverage, find_missing_tests
from tools.ail_testgen.discovery import discover_apps, discover_existing_tests
from tools.ail_testgen.generator import generate_all
from tools.ail_testgen.models import AppInfo, CoverageReport, TestCase, TestCategory
from tools.ail_testgen.reporter import generate_json_report, generate_markdown_report
from tools.ail_testgen.validator import validate_generated_tests

__all__ = [
    "TestCase",
    "TestCategory",
    "AppInfo",
    "CoverageReport",
    "discover_apps",
    "discover_existing_tests",
    "analyze_coverage",
    "find_missing_tests",
    "generate_all",
    "generate_json_report",
    "generate_markdown_report",
    "validate_generated_tests",
]

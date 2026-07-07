"""AILang Test Generator — DX-005 CLI entry point.

Usage:
    python -m tools.ail_testgen
    python -m tools.ail_testgen --app inventory
    python -m tools.ail_testgen --dry-run
    python -m tools.ail_testgen --force
    python -m tools.ail_testgen --report-only
"""

from __future__ import annotations

import sys
from pathlib import Path

from tools.ail_testgen.discovery import discover_apps, discover_existing_tests
from tools.ail_testgen.analyzer import analyze_coverage, find_missing_tests
from tools.ail_testgen.generator import generate_all
from tools.ail_testgen.validator import validate_generated_tests
from tools.ail_testgen.reporter import generate_json_report, generate_markdown_report
from tools.common.filesystem import get_project_root, ensure_output_dir
from tools.common.cli import create_parser, add_output_args, add_common_args
from tools.common.reporting import write_json_report, write_markdown_report


def build_parser():
    parser = create_parser(
        "ail_testgen",
        "AILang Test Generator — auto-discovers apps, analyzes coverage gaps, "
        "and generates pytest-compatible test files.",
    )
    add_output_args(parser)
    add_common_args(parser)
    parser.add_argument(
        "--app",
        type=str,
        default=None,
        help="Generate tests for a specific app only",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be generated without writing files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated test files",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Regenerate the report without generating test files",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    root = get_project_root()
    output_dir = Path(args.output_dir) if args.output_dir else root / "tests" / "generated"

    # Stage 1: Discovery
    if not args.quiet:
        print("Discovering apps...")
    apps = discover_apps()

    if not args.quiet:
        print("Discovering existing tests...")
    existing_tests = discover_existing_tests()

    # Filter by --app if specified
    if args.app:
        apps = [a for a in apps if a.name == args.app]
        if not apps:
            print("App not found: %s" % args.app)
            return 1

    # Stage 2: Analysis
    if not args.quiet:
        print("Analyzing coverage...")
    coverage = analyze_coverage(apps, existing_tests)

    if not args.quiet:
        print("  Coverage: %d/%d apps (%.1f%%)" % (
            coverage.apps_with_tests, coverage.apps_total, coverage.coverage_pct))
        if coverage.untested_apps and not args.quiet:
            print("  Untested: %s" % ", ".join(coverage.untested_apps[:5]))
            if len(coverage.untested_apps) > 5:
                print("    ... and %d more" % (len(coverage.untested_apps) - 5))

    # Stage 3: Generation
    generated_files: list[dict] = []
    if not args.report_only:
        missing = find_missing_tests(apps, existing_tests)

        if not args.dry_run:
            if not args.quiet:
                print("Generating test files...")
            generated_files = generate_all(missing, output_dir, force=args.force)
            generated_count = sum(1 for f in generated_files if f["status"] == "generated")
            skipped_count = sum(1 for f in generated_files if f["status"] == "skipped")
            if not args.quiet:
                print("  Generated: %d files" % generated_count)
                print("  Skipped: %d files" % skipped_count)
        else:
            if not args.quiet:
                print("Dry run: would generate %d test files" % len(missing))
            for m in missing:
                generated_files.append({
                    "file": "tests/generated/test_app_%s_generated.py" % m.app_name,
                    "app": m.app_name,
                    "status": "would_generate",
                    "test_count": 1,
                })

    # Create __init__.py in generated dir so pytest discovers it
    if not args.dry_run and not args.report_only:
        init_file = output_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("", encoding="utf-8")

    # Generate reports
    report_dir = ensure_output_dir(root / "generated")
    report = generate_json_report(coverage, generated_files)
    write_json_report(report, report_dir / "TEST_GENERATION_REPORT.json")

    markdown = generate_markdown_report(coverage, generated_files)
    write_markdown_report(markdown, report_dir / "TEST_GENERATION_REPORT.md")

    if not args.quiet:
        print("Report: generated/TEST_GENERATION_REPORT.md")
        print("Report: generated/TEST_GENERATION_REPORT.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())

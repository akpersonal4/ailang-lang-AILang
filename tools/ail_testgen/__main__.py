"""AILang Test Generator — DX-005 CLI entry point.

Usage:
    python -m tools.ail_testgen
    python -m tools.ail_testgen --app inventory
    python -m tools.ail_testgen <file.ail>
    python -m tools.ail_testgen --dry-run
    python -m tools.ail_testgen --force
    python -m tools.ail_testgen --report-only
"""

from __future__ import annotations

import sys
from pathlib import Path

from ail_platform.project import resolve_project_root
from tools.ail_testgen.analyzer import analyze_coverage, find_missing_tests
from tools.ail_testgen.discovery import discover_apps, discover_existing_tests
from tools.ail_testgen.generator import generate_all
from tools.ail_testgen.models import AppInfo
from tools.ail_testgen.reporter import generate_json_report, generate_markdown_report
from tools.common.cli import add_common_args, add_output_args, create_parser
from tools.common.filesystem import ensure_output_dir
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
        "file",
        nargs="?",
        type=Path,
        default=None,
        help="Generate tests for a single .ail source file (treats its "
             "directory as the app; overrides --app and project discovery)",
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

    # Root = the user's project directory (CWD, or the nearest ancestor with
    # an ail.toml / .ail marker). Discovery, output, and reports are scoped
    # to that project — never to the installed package location, which is
    # what a wheel install gets via __file__-based root detection.
    root = resolve_project_root()
    output_dir = (
        Path(args.output_dir) if args.output_dir else root / "tests" / "generated"
    )

    # Stage 1: Discovery
    if not args.quiet:
        print("Discovering apps...")
    # When a single file is passed positionally, skip project discovery
    # and synthesize a one-app view around that file. This makes
    # `ail testgen <file.ail>` a usable single-file mode in addition to
    # the default project-wide discovery.
    if args.file is not None:
        file_path: Path = args.file.resolve()
        if not file_path.is_file() or file_path.suffix != ".ail":
            print("Error: not an AILang source file: %s" % args.file)
            return 1
        apps = [
            AppInfo(
                name=file_path.stem,
                source_file=file_path,
                line_count=len(
                    file_path.read_text(encoding="utf-8", errors="replace").splitlines()
                ),
            )
        ]
    else:
        apps = discover_apps()
        if not apps:
            print(
                "Error: no apps discovered under the current project root "
                "(%s). Run from a directory containing an ail.toml project, "
                "or pass a positional .ail file path." % root
            )
            return 1

    if not args.quiet:
        print("Discovering existing tests...")
    existing_tests = discover_existing_tests()

    # Filter by --app if specified (skipped when a positional file narrowed
    # the scope to a single synthetic app).
    if args.app and args.file is None:
        apps = [a for a in apps if a.name == args.app]
        if not apps:
            print("App not found: %s" % args.app)
            return 1

    # Stage 2: Analysis
    if not args.quiet:
        print("Analyzing coverage...")
    coverage = analyze_coverage(apps, existing_tests)

    if not args.quiet:
        print(
            "  Coverage: %d/%d apps (%.1f%%)"
            % (coverage.apps_with_tests, coverage.apps_total, coverage.coverage_pct)
        )
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
            generated_count = sum(
                1 for f in generated_files if f["status"] == "generated"
            )
            skipped_count = sum(1 for f in generated_files if f["status"] == "skipped")
            if not args.quiet:
                print("  Generated: %d files" % generated_count)
                print("  Skipped: %d files" % skipped_count)
        else:
            if not args.quiet:
                print("Dry run: would generate %d test files" % len(missing))
            for m in missing:
                generated_files.append(
                    {
                        "file": "tests/generated/test_app_%s_generated.py" % m.app_name,
                        "app": m.app_name,
                        "status": "would_generate",
                        "test_count": 1,
                    }
                )

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

# AILang Developer Experience Tool: ail order
# Dependency Ordering Assistant - analyzes and fixes function ordering

"""AILang Dependency Ordering Assistant - analyzes .ail files for ordering issues."""

from __future__ import annotations

import sys
from pathlib import Path

from ail_platform.project import get_project_root
from ail_platform.report_schema import ExitCode
from tools.ail_order.discovery import analyze_file, discover_ail_files
from tools.ail_order.fixer import apply_fix, get_ordered_content
from tools.ail_order.graph import analyze_graph
from tools.ail_order.models import FileAnalysis, ProjectAnalysis
from tools.ail_order.reporter import (
    generate_json_report,
    write_reports,
)

VERSION = "0.1.0"


def analyze_target(target: Path) -> tuple[ProjectAnalysis | FileAnalysis, bool]:
    """Analyze the target (file or directory) and return results."""
    ail_files = discover_ail_files(target)

    if not ail_files:
        return FileAnalysis(path=str(target)), False

    if len(ail_files) == 1:
        # Single file analysis
        file_analysis = analyze_file(ail_files[0])
        analyze_graph(file_analysis)
        return file_analysis, True

    # Multiple files (project) analysis
    project = ProjectAnalysis()
    for f in ail_files:
        file_analysis = analyze_file(f)
        analyze_graph(file_analysis)
        project.files.append(file_analysis)

    project.total_functions = sum(len(fa.functions) for fa in project.files)
    project.total_findings = sum(len(fa.findings) for fa in project.files)
    project.total_cycles = sum(len(fa.cycles) for fa in project.files)

    return project, True


def print_single_file_report(analysis: FileAnalysis, quiet: bool = False) -> None:
    """Print human-readable report for single file to stdout."""
    if quiet:
        return

    print(f"\nDependency Order Analysis: {analysis.path}\n")

    # Show levels
    max_level = max(analysis.levels.keys()) if analysis.levels else 0
    for level in range(max_level + 1):
        funcs = analysis.levels.get(level, [])
        if funcs:
            print(f"L{level}:")
            for func in funcs:
                print(f"  {func}")
            print()

    # Show findings
    if analysis.findings:
        print("Findings:")
        for finding in analysis.findings:
            sev = finding.severity.value.upper()
            loc = f" (line {finding.line})" if finding.line else ""
            print(f"  [{sev}]{loc} {finding.message}")
            if finding.suggestion:
                print(f"    Suggestion: {finding.suggestion}")
    else:
        print("No ordering issues found.")


def main() -> int:
    """Main entry point for the ail order tool."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AILang Dependency Ordering Assistant - analyzes .ail source for ordering issues"
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="File or directory to analyze (.ail file, directory, or '.')",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output only JSON (machine readable)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply automatic reordering (preserves comments/formatting)",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress non-error output"
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Output reordered content to stdout (use with --fix)",
    )

    args = parser.parse_args()

    root = get_project_root()

    # Resolve target path
    target_path = Path(args.target)
    if not target_path.is_absolute():
        target_path = root / target_path

    if not target_path.exists():
        print(f"Error: Not found: {target_path}", file=sys.stderr)
        return ExitCode.INTERNAL_ERROR

    analysis, success = analyze_target(target_path)

    if not success:
        print(f"Error: No .ail files found in {target_path}", file=sys.stderr)
        return ExitCode.FAILURE

    # Apply fix if requested
    if args.fix:
        if isinstance(analysis, ProjectAnalysis):
            print("Error: --fix only works on single files", file=sys.stderr)
            return ExitCode.FAILURE

        if args.stdout:
            content = target_path.read_text(encoding="utf-8")
            print(get_ordered_content(content, analysis.levels))
        else:
            changed = apply_fix(target_path, analysis)
            if changed and not args.quiet:
                print(f"Reordered: {target_path}")

    # Output
    if isinstance(analysis, ProjectAnalysis):
        # Multi-file report
        output_dir = root / "reports"
        md_path, json_path = write_reports(analysis, output_dir)

        if not args.quiet:
            print(f"Analyzed {len(analysis.files)} files")
            print(f"Total functions: {analysis.total_functions}")
            print(f"Total findings: {analysis.total_findings}")
            print(f"Generated: {md_path}")
            print(f"Generated: {json_path}")
    else:
        # Single file report
        if args.json:
            print(generate_json_report(analysis))
        elif args.fix and args.stdout:
            # Already output above
            pass
        else:
            print_single_file_report(analysis, args.quiet)

    # Determine exit code
    if isinstance(analysis, FileAnalysis):
        has_errors = any(
            f.severity == analysis.findings[0].severity if analysis.findings else None
            for f in analysis.findings
        )
        for f in analysis.findings:
            if f.severity.value == "error":
                return ExitCode.FAILURE

    return ExitCode.SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())

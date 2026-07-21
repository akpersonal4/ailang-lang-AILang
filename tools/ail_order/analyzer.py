"""AILang Dependency Ordering Assistant - Analysis orchestration.

This module provides the main analysis entry point combining discovery and graph analysis.
"""

from __future__ import annotations

from pathlib import Path

from tools.ail_order.discovery import analyze_file, discover_ail_files
from tools.ail_order.graph import analyze_graph
from tools.ail_order.models import FileAnalysis, ProjectAnalysis


def analyze(target: Path | str) -> ProjectAnalysis | FileAnalysis:
    """Analyze a file or directory for dependency ordering issues.

    Args:
        target: Path to .ail file or directory containing .ail files

    Returns:
        FileAnalysis for single file, ProjectAnalysis for multiple files
    """
    target_path = Path(target) if not isinstance(target, Path) else target

    if not target_path.exists():
        raise FileNotFoundError(f"Not found: {target_path}")

    ail_files = discover_ail_files(target_path)

    if not ail_files:
        raise ValueError(f"No .ail files found in {target_path}")

    if len(ail_files) == 1:
        file_analysis = analyze_file(ail_files[0])
        analyze_graph(file_analysis)
        return file_analysis

    # Multiple files - project analysis
    project = ProjectAnalysis()
    for f in ail_files:
        file_analysis = analyze_file(f)
        analyze_graph(file_analysis)
        project.files.append(file_analysis)

    project.total_functions = sum(len(fa.functions) for fa in project.files)
    project.total_findings = sum(len(fa.findings) for fa in project.files)
    project.total_cycles = sum(len(fa.cycles) for fa in project.files)

    return project

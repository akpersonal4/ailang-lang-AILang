"""AILang Dependency Ordering Assistant - Data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    """Finding severity levels."""
    ERROR = "error"
    WARNING = "warning"
    RECOMMENDATION = "recommendation"
    INFO = "info"


@dataclass
class FunctionInfo:
    """Information about a function definition."""
    name: str
    line: int
    start_line: int
    end_line: int
    parameters: list[str] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)
    level: int = 0  # Topological level
    has_doc_comment: bool = False


@dataclass
class OrderingFinding:
    """A finding from dependency analysis."""
    severity: Severity
    message: str
    line: int | None = None
    function: str | None = None
    suggestion: str | None = None


@dataclass
class FileAnalysis:
    """Analysis result for a single .ail file."""
    path: str
    functions: list[FunctionInfo] = field(default_factory=list)
    findings: list[OrderingFinding] = field(default_factory=list)
    cycles: list[list[str]] = field(default_factory=list)
    levels: dict[int, list[str]] = field(default_factory=dict)
    forward_refs: list[tuple[str, str, int]] = field(default_factory=list)  # (caller, callee, line)
    unreachable: list[str] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)


@dataclass
class ProjectAnalysis:
    """Analysis result for a project (multiple files)."""
    files: list[FileAnalysis] = field(default_factory=list)
    total_functions: int = 0
    total_findings: int = 0
    total_cycles: int = 0
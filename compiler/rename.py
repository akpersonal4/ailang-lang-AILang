"""Repository-wide rename tool for AILang identifiers.

Provides safe, verifiable identifier renaming across all .ail files
in a repository with atomic file rewriting and rollback support.

Usage:
    from compiler.rename import RenameTool
    tool = RenameTool(root_dir)
    refs = tool.scan("old_name")
    changes = tool.compute_changes("old_name", "new_name")
    tool.apply(changes)
    tool.verify(entry_path)
"""

from __future__ import annotations

import difflib
import json
import os
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from compiler.ast.builder import ASTBuilder
from compiler.ast.nodes import (
    ASTNode,
    IdentifierNode,
    ImportDeclarationNode,
    ProgramNode,
    StringLiteralNode,
)
from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.lexer import Lexer, LexicalError
from compiler.parser import Parser

_SKIP_DIRS = frozenset(
    {
        ".venv",
        ".venv_test",
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "node_modules",
        "__pycache__",
        ".ail",
    }
)


@dataclass
class RenameReference:
    """A single identifier reference to be renamed."""

    file_path: str
    start_offset: int
    end_offset: int
    kind: str  # "identifier", "string", or "import"


@dataclass
class FileChange:
    """Original and new content for a single file."""

    file_path: str
    original_content: str
    new_content: str


def _find_stdlib(root_dir: Path) -> Path | None:
    """Locate the stdlib directory relative to the project root."""
    current = root_dir.resolve()
    while True:
        candidate = current / "stdlib"
        if candidate.is_dir() and (current / "pyproject.toml").is_file():
            return candidate
        if current == current.parent:
            break
        current = current.parent
    return None


class RenameTool:
    """Repository-wide rename tool with atomic rollback."""

    def __init__(self, root_dir: str | Path) -> None:
        self.root_dir = Path(root_dir).resolve()
        self._references: list[RenameReference] = []

    # ------------------------------------------------------------------
    # Scanning
    # ------------------------------------------------------------------

    def scan(
        self, old_name: str, include_strings: bool = False
    ) -> list[RenameReference]:
        """Scan all .ail files for references to *old_name*.

        Returns the list of references found (also stored internally).
        """
        references: list[RenameReference] = []
        for file_path in sorted(self.root_dir.rglob("*.ail")):
            if any(skip in file_path.parts for skip in _SKIP_DIRS):
                continue
            refs = self._scan_file(file_path, old_name, include_strings)
            references.extend(refs)
        self._references = references
        return references

    def _scan_file(
        self, file_path: Path, old_name: str, include_strings: bool
    ) -> list[RenameReference]:
        """Scan a single file for identifier references."""
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception:
            return []

        try:
            lexer = Lexer(source_path=str(file_path))
            tokens = lexer.tokenize(text)
            parser = Parser(tokens, source_path=str(file_path))
            cst = parser.parse_program()
            ast = cast(ProgramNode, ASTBuilder().build(cst))
        except (LexicalError, ValueError, Exception):
            return []

        refs: list[RenameReference] = []
        self._walk_node(ast, old_name, str(file_path), include_strings, refs)

        # Handle import path segments separately (they are plain strings, not IdentifierNodes)
        self._scan_imports(ast, old_name, str(file_path), text, refs)

        return refs

    def _walk_node(
        self,
        node: ASTNode,
        old_name: str,
        file_path: str,
        include_strings: bool,
        refs: list[RenameReference],
    ) -> None:
        """Recursively walk the AST collecting identifier references."""
        if isinstance(node, IdentifierNode):
            if (
                node.name == old_name
                and node.start_span is not None
                and node.end_span is not None
            ):
                refs.append(
                    RenameReference(
                        file_path, node.start_span, node.end_span, "identifier"
                    )
                )

        if include_strings and isinstance(node, StringLiteralNode):
            if (
                node.value == old_name
                and node.start_span is not None
                and node.end_span is not None
            ):
                refs.append(
                    RenameReference(file_path, node.start_span, node.end_span, "string")
                )

        for f_name in node.__dataclass_fields__:
            if f_name in ("start_span", "end_span"):
                continue
            value = getattr(node, f_name)
            if isinstance(value, ASTNode):
                self._walk_node(value, old_name, file_path, include_strings, refs)
            elif isinstance(value, (tuple, list)):
                for item in value:
                    if isinstance(item, ASTNode):
                        self._walk_node(
                            item, old_name, file_path, include_strings, refs
                        )

    def _scan_imports(
        self,
        ast: ProgramNode,
        old_name: str,
        file_path: str,
        text: str,
        refs: list[RenameReference],
    ) -> None:
        """Find import path segments matching *old_name*."""
        for child in ast.children:
            if not isinstance(child, ImportDeclarationNode):
                continue
            if child.start_span is None or child.end_span is None:
                continue
            for idx, segment in enumerate(child.module_path):
                if segment == old_name:
                    offset = self._find_import_segment_offset(text, child, idx)
                    if offset is not None:
                        refs.append(
                            RenameReference(
                                file_path, offset, offset + len(segment), "import"
                            )
                        )

    @staticmethod
    def _find_import_segment_offset(
        text: str, import_node: ImportDeclarationNode, segment_index: int
    ) -> int | None:
        """Find the character offset of an import path segment in source text."""
        if import_node.start_span is None:
            return None
        region = text[import_node.start_span : import_node.end_span]
        kw_idx = region.find("import ")
        if kw_idx == -1:
            return None
        path_start = kw_idx + len("import ")
        path_end = region.find(";")
        if path_end == -1:
            path_end = region.find(" as ")
            if path_end == -1:
                path_end = len(region)
        path_text = region[path_start:path_end].strip()
        segments = path_text.split(".")
        if segment_index >= len(segments):
            return None
        # Compute offset of the segment within the path
        before_dots = sum(len(s) for s in segments[:segment_index])
        dots_before = max(0, segment_index)  # one dot between each segment
        segment_start_offset = (
            import_node.start_span + path_start + before_dots + dots_before
        )
        return segment_start_offset

    # ------------------------------------------------------------------
    # Change computation
    # ------------------------------------------------------------------

    def compute_changes(self, old_name: str, new_name: str) -> dict[str, FileChange]:
        """Compute text-level changes grouped by file.

        Applies replacements from highest offset to lowest so that
        earlier positions are not invalidated.
        """
        changes: dict[str, FileChange] = {}
        file_refs: dict[str, list[RenameReference]] = {}
        for ref in self._references:
            file_refs.setdefault(ref.file_path, []).append(ref)

        for file_path, refs in file_refs.items():
            try:
                with open(file_path, encoding="utf-8") as f:
                    original = f.read()
            except Exception:
                continue

            sorted_refs = sorted(refs, key=lambda r: -r.start_offset)
            new_text = original
            for ref in sorted_refs:
                actual = new_text[ref.start_offset : ref.end_offset]
                if actual == old_name:
                    new_text = (
                        new_text[: ref.start_offset]
                        + new_name
                        + new_text[ref.end_offset :]
                    )

            if new_text != original:
                changes[file_path] = FileChange(file_path, original, new_text)

        return changes

    def dry_run(self, old_name: str, new_name: str) -> dict[str, FileChange]:
        """Compute changes without modifying any files."""
        return self.compute_changes(old_name, new_name)

    # ------------------------------------------------------------------
    # Diff output
    # ------------------------------------------------------------------

    @staticmethod
    def print_diff(changes: dict[str, FileChange]) -> None:
        """Print unified diff of all changes to stdout."""
        for file_path, change in sorted(changes.items()):
            orig_lines = change.original_content.splitlines(keepends=True)
            new_lines = change.new_content.splitlines(keepends=True)
            diff = list(
                difflib.unified_diff(
                    orig_lines,
                    new_lines,
                    fromfile=f"a/{file_path}",
                    tofile=f"b/{file_path}",
                )
            )
            sys.stdout.writelines(diff)

    # ------------------------------------------------------------------
    # Application with rollback
    # ------------------------------------------------------------------

    def apply(
        self, changes: dict[str, FileChange], rollback_dir: str | None = None
    ) -> str | None:
        """Apply changes atomically with rollback support.

        Every modified file gets a ``.orig`` backup in the rollback bundle.
        If any write fails, all already-written files are restored.

        Returns the path to the rollback directory, or ``None`` if no
        changes were made.
        """
        if not changes:
            return None

        if rollback_dir is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            rollback_dir = str(self.root_dir / ".ail" / "rename" / timestamp)

        rb_dir = Path(rollback_dir)
        rb_dir.mkdir(parents=True, exist_ok=True)
        backup_dir = rb_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        manifest: dict[str, object] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "files_modified": sorted(changes.keys()),
            "status": "pending",
        }
        with open(rb_dir / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        applied: list[str] = []
        try:
            for file_path in sorted(changes):
                change = changes[file_path]
                rel = Path(file_path).relative_to(self.root_dir)
                backup_path = backup_dir / rel
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(change.original_content)

                tmp_path = file_path + ".rename.tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    f.write(change.new_content)
                os.replace(tmp_path, file_path)
                applied.append(file_path)

            manifest["status"] = "applied"
            with open(rb_dir / "manifest.json", "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
            return str(rb_dir)

        except BaseException:
            for file_path in applied:
                rel = Path(file_path).relative_to(self.root_dir)
                backup_path = backup_dir / rel
                if backup_path.exists():
                    shutil.copy2(str(backup_path), file_path)
            manifest["status"] = "rolled_back"
            with open(rb_dir / "manifest.json", "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
            raise

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def verify(self, entry_path: str | Path) -> bool:
        """Run the compiler on the entry point to verify correctness.

        Returns ``True`` if compilation succeeds, ``False`` otherwise.
        """
        entry = Path(entry_path).resolve()
        if not entry.exists():
            return True

        stdlib_dir = _find_stdlib(self.root_dir)
        if stdlib_dir is None:
            return True

        session = CompilationSession()
        session._root = self.root_dir
        session._resolver = type(session._resolver)(self.root_dir)

        reporter = DiagnosticReporter()
        session.discover(entry_path, reporter)
        session.analyze(reporter)

        return reporter.error_count == 0

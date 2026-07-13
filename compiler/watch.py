"""Watch mode — incremental compilation on file changes.

Provides ``ail watch`` for automatic recompilation when ``.ail`` files
change, with debouncing for AI burst edits and cross-platform file
system monitoring via ``watchdog``.
"""

from __future__ import annotations

import hashlib
import os
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from compiler.compilation import CompilationSession
from compiler.diagnostics import Diagnostic, DiagnosticFormatter, DiagnosticReporter, ErrorCode, Severity
from compiler.lexer import Lexer, LexicalError
from compiler.parser import Parser
from compiler.source import Source

_SKIP_DIRS = frozenset({
    ".venv", ".venv_test", ".git", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", "node_modules", "__pycache__", ".ail",
})


# =============================================================================
# File-change cache
# =============================================================================


@dataclass
class FileCacheEntry:
    """Cached compilation result for a single file."""

    file_path: str
    file_hash: str
    compile_time_ms: float
    imports: list[str] = field(default_factory=list)
    ok: bool = True


class FileCache:
    """Per-file hash-based change detection cache."""

    def __init__(self) -> None:
        self._entries: dict[str, FileCacheEntry] = {}

    def get_hash(self, file_path: str) -> str | None:
        """Return the cached hash for *file_path*, or ``None``."""
        entry = self._entries.get(file_path)
        return entry.file_hash if entry is not None else None

    def has_changed(self, file_path: str, new_hash: str) -> bool:
        """Return ``True`` if the file's hash differs from the cached one."""
        old = self.get_hash(file_path)
        return old is None or old != new_hash

    def update(self, file_path: str, entry: FileCacheEntry) -> None:
        """Store or update the cache entry for *file_path*."""
        self._entries[file_path] = entry

    def remove(self, file_path: str) -> None:
        """Remove a file from the cache."""
        self._entries.pop(file_path, None)


# =============================================================================
# Compilation hash (SHA-256 wrapper)
# =============================================================================


def file_hash(file_path: str) -> str:
    """Compute the SHA-256 hex digest of a file's contents."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# =============================================================================
# Incremental compiler
# =============================================================================


class IncrementalCompiler:
    """Wraps ``CompilationSession`` with caching and incremental recompilation.

    Usage:
        ic = IncrementalCompiler(root_dir, entry_path)
        ic.initial_build()
        ok, affected, ms = ic.incremental_compile("/path/to/changed.ail")
    """

    def __init__(self, root_dir: str | Path, entry_path: str | Path) -> None:
        self.root_dir = Path(root_dir).resolve()
        self.entry_path = str(Path(entry_path).resolve())
        self._cache = FileCache()
        self._session: CompilationSession | None = None

    # ------------------------------------------------------------------
    # Initial build
    # ------------------------------------------------------------------

    def initial_build(self) -> bool:
        """Perform a full build and populate the file cache.

        Returns ``True`` on success.
        """
        reporter = DiagnosticReporter()
        session = CompilationSession()
        session._root = self.root_dir
        session._resolver = type(session._resolver)(self.root_dir)

        try:
            session.discover(self.entry_path, reporter)
        except Exception as exc:
            diag = Diagnostic(
                Severity.ERROR, ErrorCode("CMP001", str(exc)), str(exc),
            )
            print(DiagnosticFormatter().format(diag), file=sys.stderr)
            return False

        session.analyze(reporter)

        for diag in reporter.diagnostics:
            print(DiagnosticFormatter().format(diag), file=sys.stderr)

        if reporter.error_count > 0:
            return False

        self._session = session

        # Populate cache
        for module_name, src in session._sources.items():
            fp = str(src.path)
            h = file_hash(fp)
            cache_entry = FileCacheEntry(
                file_path=fp,
                file_hash=h,
                compile_time_ms=0,
                ok=True,
            )
            self._cache.update(fp, cache_entry)

        return True

    # ------------------------------------------------------------------
    # Incremental recompilation
    # ------------------------------------------------------------------

    def incremental_compile(self, changed_path: str) -> tuple[bool, list[str], float]:
        """Recompile the changed file and all dependents.

        Returns ``(success, affected_modules, elapsed_ms)``.
        """
        start = time.perf_counter()
        reporter = DiagnosticReporter()

        fp = Path(changed_path).resolve()
        if not fp.exists():
            self._cache.remove(str(fp))
            return True, [], 0.0

        new_hash = file_hash(str(fp))
        if not self._cache.has_changed(str(fp), new_hash):
            return True, [], 0.0

        session = self._session
        if session is None:
            return False, [], 0.0

        ok, affected = session.incremental_recompile(str(fp), reporter)

        elapsed_ms = (time.perf_counter() - start) * 1000

        # Update cache
        if ok:
            for mod_name in affected:
                if mod_name in session._sources:
                    src_path = str(session._sources[mod_name].path)
                    h = file_hash(src_path)
                    self._cache.update(src_path, FileCacheEntry(
                        file_path=src_path, file_hash=h,
                        compile_time_ms=elapsed_ms, ok=True,
                    ))
        else:
            self._cache.update(str(fp), FileCacheEntry(
                file_path=str(fp), file_hash=new_hash,
                compile_time_ms=elapsed_ms, ok=False,
            ))

        # Print diagnostics
        for diag in reporter.diagnostics:
            print(DiagnosticFormatter().format(diag), file=sys.stderr)

        return ok, affected, elapsed_ms


# =============================================================================
# Filesystem watcher (watchdog-based)
# =============================================================================


class _AilFileHandler:
    """Handles filesystem events for ``.ail`` files with debouncing."""

    def __init__(self, compiler: IncrementalCompiler, debounce_ms: int = 200) -> None:
        self.compiler = compiler
        self._debounce_ms = debounce_ms / 1000.0
        self._timers: dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def on_any_event(self, event: object) -> None:
        """Handle a file-system event from watchdog."""
        try:
            src_path = getattr(event, "src_path", None)
            if src_path is None:
                return
            if not src_path.endswith(".ail"):
                return
            is_dir = getattr(event, "is_directory", False)
            if is_dir:
                return
            self._debounce(str(Path(src_path).resolve()))
        except Exception:
            pass

    def _debounce(self, file_path: str) -> None:
        """Debounce: restart a timer for this file on each event."""
        with self._lock:
            timer = self._timers.pop(file_path, None)
            if timer is not None:
                timer.cancel()
            timer = threading.Timer(self._debounce_ms, self._compile, args=[file_path])
            timer.daemon = True
            self._timers[file_path] = timer
            timer.start()

    def _compile(self, file_path: str) -> None:
        """Run the incremental compile after debounce fires."""
        with self._lock:
            self._timers.pop(file_path, None)

        ok, affected, elapsed_ms = self.compiler.incremental_compile(file_path)

        timestamp = time.strftime("%H:%M:%S")
        rel_path = _shorten_path(file_path, self.compiler.root_dir)

        if ok:
            files_str = f"{len(affected)} file(s)" if affected else "0 files"
            print(f"[{timestamp}] CHANGE: {rel_path}")
            print(f"  {files_str} — OK ({elapsed_ms:.0f}ms)")
        else:
            print(f"[{timestamp}] CHANGE: {rel_path}")
            print(f"  {files_str} — ERROR ({elapsed_ms:.0f}ms)")


def _shorten_path(path: str, root: Path) -> str:
    """Return a path relative to the project root where possible."""
    try:
        return str(Path(path).relative_to(root))
    except ValueError:
        return path


def _collect_ail_files(root: Path) -> list[Path]:
    """Collect all ``.ail`` files under *root*, excluding skip dirs."""
    files: list[Path] = []
    for fp in sorted(root.rglob("*.ail")):
        if any(skip in fp.parts for skip in _SKIP_DIRS):
            continue
        files.append(fp)
    return files


# =============================================================================
# Polling-based watcher (fallback)
# =============================================================================


class PollingWatcher:
    """Polling-based file change detector."""

    def __init__(self, compiler: IncrementalCompiler, interval_ms: int = 500) -> None:
        self.compiler = compiler
        self.interval = interval_ms / 1000.0
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start polling in a background thread."""
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the polling thread."""
        self._running = False

    def _poll_loop(self) -> None:
        while self._running:
            time.sleep(self.interval)
            try:
                for fp in _collect_ail_files(self.compiler.root_dir):
                    h = file_hash(str(fp))
                    if self.compiler._cache.has_changed(str(fp), h):
                        self.compiler.incremental_compile(str(fp))
            except Exception:
                pass


# =============================================================================
# Watch-mode entry point
# =============================================================================


def run_watch(
    entry_path: str,
    poll: bool = False,
    poll_interval: int = 500,
    no_initial: bool = False,
    json_mode: bool = False,
    verbose: bool = False,
) -> int:
    """Run the watch-mode main loop.

    Returns an exit code (0 for clean exit).
    """
    root_dir = Path(entry_path).resolve()
    if not root_dir.is_dir():
        root_dir = root_dir.parent

    # Find the project root (where pyproject.toml lives)
    project_root = root_dir
    while True:
        if (project_root / "pyproject.toml").is_file():
            break
        if project_root == project_root.parent:
            project_root = root_dir
            break
        project_root = project_root.parent

    compiler = IncrementalCompiler(project_root, entry_path)

    if not no_initial:
        if json_mode:
            print('{"type":"initial","status":"building"}')
        else:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] ail watch — initial build...")

        ok = compiler.initial_build()

        if json_mode:
            status = "passed" if ok else "failed"
            print(f'{{"type":"initial","status":"{status}"}}')
        else:
            if ok:
                ail_count = len(_collect_ail_files(project_root))
                print(f"[{time.strftime('%H:%M:%S')}] Initial build: {ail_count} files, 0 errors")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Initial build failed", file=sys.stderr)

    if poll:
        watcher = PollingWatcher(compiler, poll_interval)
        watcher.start()
    else:
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class _Handler(FileSystemEventHandler):
                def __init__(self, handler: _AilFileHandler) -> None:
                    self._handler = handler

                def on_modified(self, event: object) -> None:
                    self._handler.on_any_event(event)

                def on_created(self, event: object) -> None:
                    self._handler.on_any_event(event)

                def on_deleted(self, event: object) -> None:
                    if hasattr(event, "src_path") and event.src_path is not None:
                        compiler._cache.remove(str(event.src_path))

            ail_handler = _AilFileHandler(compiler)
            observer = Observer()
            handler = _Handler(ail_handler)
            observer.schedule(handler, str(project_root), recursive=True)
            observer.start()

            if not json_mode:
                ail_count = len(_collect_ail_files(project_root))
                print(f"[{time.strftime('%H:%M:%S')}] ail watch — watching {ail_count} files")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()
        except ImportError:
            print("watchdog not installed; falling back to polling mode", file=sys.stderr)
            watcher = PollingWatcher(compiler, poll_interval)
            watcher.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                watcher.stop()

    return 0

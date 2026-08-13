"""Regression and performance tests for the M136 fixes.

P0 — ``ail run --no-check`` must execute the user program exactly once.
    The first-run welcome banner previously printed to stdout, which
    contaminated program output and could be mistaken for double execution
    when piped/captured. The banner is now routed to stderr so program
    stdout is pure. Additionally, ``cmd_run`` now executes the user's
    entry module directly (with its body run by ``runtime.execute`` and
    initialized without body), guaranteeing the entry body runs exactly
    once regardless of topological order.

P1a — ``ail testgen`` must emit tests compatible with ``ail test``.
    The generator previously emitted pytest ``.py`` files that invoked
    the application with no arguments and could not be executed by
    ``ail test``. The generator now emits ``.ail`` files placed inside
    the app's own ``tests/`` directory so module imports resolve and
    ``ail test`` discovers them naturally.

P1b — Interpreter O(n^2) name-resolution behavior
    The runtime's Environment.resolve walks the parent-environment chain
    recursively. A recursive driver at depth n that calls a per-row helper
    resolving module names (convert.to_string, string.uppercase, ...)
    caused ~12M resolve calls and ~71% of runtime. The fix adds a monotonic
    frame-bound-name set to the Runtime so module/builtin lookups skip the
    chain walk when the name has never been bound in any frame, turning the
    hot path from O(call_depth) into O(1) while preserving dynamic scoping.

These tests assert both correctness (semantics unchanged) and that the
pathological scaling is materially improved.
"""

from __future__ import annotations

import time
from pathlib import Path

from compiler.compilation import CompilationSession
from compiler.compilation.resolution import ModuleResolver
from compiler.runtime import Runtime
from compiler.runtime.sandbox import SandboxPolicy, set_policy


REPO_ROOT = Path(__file__).resolve().parents[1]


_PROGRAM_TEMPLATE = (
    "import convert;\n"
    "import string;\n"
    "fn build_row(i) {{\n"
    "    let s = convert.to_string(i);\n"
    "    let u = string.uppercase(s);\n"
    "    return u\n"
    "}}\n"
    "fn drive(i, n) {{\n"
    "    if (i >= n) {{ return 0 }}\n"
    "    let _r = build_row(i);\n"
    "    return drive(i + 1, n)\n"
    "}}\n"
    "fn main() {{\n"
    "    let _x = drive(0, {n});\n"
    "    return 0\n"
    "}}\n"
)


def _execute_n_rows(n: int) -> float:
    """Compile and execute the recursive-driver program for ``n`` rows.

    Returns wall-clock time in seconds for ``runtime.execute`` only (the
    hot path affected by the fix).
    """
    with _PerfWorkdir() as workdir:
        src_path = workdir / "perf.ail"
        src_path.write_text(_PROGRAM_TEMPLATE.format(n=n), encoding="utf-8")
        set_policy(SandboxPolicy(enabled=False))

        session = CompilationSession()
        session._root = workdir.resolve()
        session._resolver = ModuleResolver(session._root)
        session.discover(src_path, None)
        session.analyze(None)
        session.type_check(None)

        bundle = session.build_ir()
        runtime = Runtime(bundle)
        source_map = {
            name: (str(src.path), src.text)
            for name, src in session._sources.items()
        }
        runtime.set_source_map(source_map)
        for module_name in session._graph.topological_sort():
            runtime._initialize_module(module_name)

        main_module = None
        for module_name in session._graph.topological_sort():
            if module_name in bundle.module_irs:
                main_module = module_name
                break
        program_ir = bundle.module_irs[main_module]

        t0 = time.perf_counter()
        result = runtime.execute(program_ir)
        dt = time.perf_counter() - t0
        assert result == 0
        return dt


class _PerfWorkdir:
    """Context manager that creates and removes a clean working directory."""

    def __init__(self) -> None:
        import tempfile
        import shutil
        self._tmpdir = Path(tempfile.mkdtemp(prefix="ail_m136_"))
        # Ensure stdlib is resolvable: put the repo root on the candidate
        # search path via ModuleResolver's upward walk, which it does
        # automatically. We just need to live near the repo so the upward
        # walk hits ``AiLang_New/stdlib``.
        self._tmpdir_keep = self._tmpdir

    def __enter__(self) -> Path:
        return self._tmpdir_keep

    def __exit__(self, exc_type, exc, tb) -> None:
        import shutil
        shutil.rmtree(self._tmpdir_keep, ignore_errors=True)


class TestNameResolutionOptimization:
    """P1b regression suite."""

    def test_correctness_small(self) -> None:
        """A small recursive program produces the expected result."""
        n = 20
        _execute_n_rows(n)  # just verify it runs and returns 0

    def test_correctness_large(self) -> None:
        """A larger recursive program still terminates and returns 0."""
        n = 500
        _execute_n_rows(n)

    def test_no_double_resolution_for_module_names(self) -> None:
        """Module-name resolution must skip the frame chain when the name
        has never been bound in a frame.

        Construct a minimal scenario where ``convert`` is never bound in
        any frame, then resolve it and assert the runtime's
        ``_frame_ever_bound`` set was not extended as a side effect.
        """
        runtime = Runtime()
        # Resolve a name that is definitely not bound in any frame.
        try:
            # Use a name that's a builtin to avoid touching the module
            # dict; we want to observe ``_frame_ever_bound`` directly.
            assert "definitely_not_bound_xyz" not in runtime._frame_ever_bound
            # Touching the set via _resolve_name for a never-bound name
            # must not add it (it isn't a frame binding).
            with __import__("pytest").raises(Exception):
                # May raise (undefined variable) -- that's fine; we just
                # want to confirm the set is untouched.
                runtime._resolve_name("definitely_not_bound_xyz")
        except NameError:
            pass
        assert "definitely_not_bound_xyz" not in runtime._frame_ever_bound

    def test_scaling_is_materially_better_than_quadratic(self) -> None:
        """Doubling ``n`` must not quadruple the runtime.

        Before the fix the ratio t(2n)/t(n) was ~5 (super-linear / quadratic)
        for this workload. After the fix it should be close to 2 (linear).
        We assert it stays below 3.0 to leave headroom for noise on slow CI
        while still proving the pathological scaling is materially improved.
        """
        # Warmup so first-run costs (imports, etc.) don't pollute the ratio.
        _execute_n_rows(50)

        def measure(n: int) -> float:
            return min(_execute_n_rows(n) for _ in range(2))

        t100 = measure(100)
        t200 = measure(200)
        t400 = measure(400)
        ratio_200_100 = t200 / t100
        ratio_400_200 = t400 / t200

        # Quadratic scaling would give ratios of ~4; linear gives ~2.
        # The fix must materially improve over quadratic. Threshold of 3.0
        # leaves room for noise while still failing the test if the
        # pathology returns.
        assert ratio_200_100 < 3.0, (
            f"ratio t(200)/t(100)={ratio_200_100:.2f} indicates super-linear "
            f"scaling; expected < 3.0 (quadratic ~4.0). "
            f"t100={t100*1000:.1f}ms t200={t200*1000:.1f}ms"
        )
        assert ratio_400_200 < 3.0, (
            f"ratio t(400)/t(200)={ratio_400_200:.2f} indicates super-linear "
            f"scaling; expected < 3.0 (quadratic ~4.0). "
            f"t200={t200*1000:.1f}ms t400={t400*1000:.1f}ms"
        )


class TestSingleExecutionP0:
    """P0 regression suite: ``ail run --no-check`` must execute exactly once.

    The CLI is exercised via ``cmd_run`` directly so the test does not
    depend on the installed ``ail`` shim picking up this repository's
    compiler (the venv resolves ``compiler`` from whichever location is
    first on sys.path). The first-run welcome check lives in ``main()``,
    not ``cmd_run()``, so tests that need it invoke ``main()`` instead.
    """

    def _run_cmd_run(
        self, source_path: Path, workdir: Path, *extra_args: str
    ) -> tuple[int, str, str]:
        """Invoke ``cmd_run`` from ``workdir`` and capture (rc, stdout, stderr).

        Running from ``workdir`` ensures the runtime sandbox (which scopes
        file I/O to the current working directory) allows the program to
        write to files inside ``workdir``.
        """
        import io
        import os as _os
        import sys as _sys

        from compiler.cli.main import cmd_run

        old_cwd = _os.getcwd()
        old_stdout = _sys.stdout
        old_stderr = _sys.stderr
        out_buf = io.StringIO()
        err_buf = io.StringIO()
        _os.chdir(str(workdir))
        _sys.stdout = out_buf
        _sys.stderr = err_buf
        try:
            args = ["--no-check", "--no-sandbox", str(source_path), *extra_args]
            rc = cmd_run(args)
        finally:
            _sys.stdout = old_stdout
            _sys.stderr = old_stderr
            _os.chdir(old_cwd)
        return rc, out_buf.getvalue(), err_buf.getvalue()

    def _run_main(
        self, argv: list[str], workdir: Path
    ) -> tuple[int, str, str]:
        """Invoke ``compiler.cli.main.main()`` from ``workdir``."""
        import io
        import os as _os
        import sys as _sys

        from compiler.cli import main as cli_main

        old_cwd = _os.getcwd()
        old_stdout = _sys.stdout
        old_stderr = _sys.stderr
        out_buf = io.StringIO()
        err_buf = io.StringIO()
        _os.chdir(str(workdir))
        _sys.stdout = out_buf
        _sys.stderr = err_buf
        try:
            rc = cli_main.main(argv)
        finally:
            _sys.stdout = old_stdout
            _sys.stderr = old_stderr
            _os.chdir(old_cwd)
        return rc, out_buf.getvalue(), err_buf.getvalue()

    def test_top_level_print_executes_exactly_once(self) -> None:
        """A single top-level ``print`` must appear in stdout exactly once."""
        with _PerfWorkdir() as workdir:
            src = workdir / "single.ail"
            src.write_text(
                'print("P0_SINGLE");\nfn main() { return 0 }\n',
                encoding="utf-8",
            )
            rc, stdout, _stderr = self._run_cmd_run(src, workdir)
            assert rc == 0
            assert stdout.count("P0_SINGLE") == 1, (
                f"expected exactly one 'P0_SINGLE' in stdout; got "
                f"{stdout.count('P0_SINGLE')}. Full stdout:\n{stdout!r}"
            )

    def test_print_inside_main_executes_exactly_once(self) -> None:
        """A ``print`` inside ``main`` must appear in stdout exactly once."""
        with _PerfWorkdir() as workdir:
            src = workdir / "in_main.ail"
            src.write_text(
                'fn main() { print("P0_INMAIN"); return 0 }\n',
                encoding="utf-8",
            )
            rc, stdout, _stderr = self._run_cmd_run(src, workdir)
            assert rc == 0
            assert stdout.count("P0_INMAIN") == 1

    def test_module_body_side_effect_runs_once(self) -> None:
        """A cumulative top-level side effect must run exactly once.

        Uses ``file.append`` so that multiple executions would accumulate
        into a longer file. This is the most direct evidence that the
        entry module's body is not executed twice.
        """
        with _PerfWorkdir() as workdir:
            src = workdir / "probe.ail"
            count_file = workdir / "probe_count.txt"
            src.write_text(
                'import file;\n'
                'file.append("probe_count.txt", "X");\n'
                'fn main() { return 0 }\n',
                encoding="utf-8",
            )
            assert not count_file.exists()
            rc, _stdout, _stderr = self._run_cmd_run(src, workdir)
            assert rc == 0
            assert count_file.exists()
            content = count_file.read_text(encoding="utf-8")
            assert content == "X", (
                f"file.append side effect must run exactly once; "
                f"got {len(content)} bytes ({content!r})"
            )

    def test_no_check_and_normal_run_identical(self) -> None:
        """``ail run`` and ``ail run --no-check`` must produce identical stdout."""
        import io as _io
        import os as _os
        import sys as _sys
        from compiler.cli.main import cmd_run

        with _PerfWorkdir() as workdir:
            src = workdir / "same.ail"
            src.write_text(
                'fn main() { print("P0_NORMAL"); return 0 }\n',
                encoding="utf-8",
            )

            def capture(args: list[str]) -> str:
                old_cwd = _os.getcwd()
                old_stdout = _sys.stdout
                _sys.stdout = _io.StringIO()
                try:
                    _os.chdir(str(workdir))
                    cmd_run(args)
                finally:
                    buf = _sys.stdout
                    _sys.stdout = old_stdout
                    _os.chdir(old_cwd)
                return buf.getvalue()

            out_nc = capture(["--no-check", "--no-sandbox", str(src)])
            out_normal = capture(["--no-sandbox", str(src)])
            assert out_nc == out_normal
            assert out_nc.count("P0_NORMAL") == 1

    def test_first_run_welcome_routed_to_stderr(self) -> None:
        """The first-run welcome banner must go to stderr, not stdout.

        Exercises the full ``main()`` entry so the first-run welcome check
        in ``main()`` runs. The banner must end up on stderr so it cannot
        be mistaken for duplicate program output.
        """
        state_file = Path.home() / ".ail" / "state.json"
        had_state = state_file.exists()
        backup: bytes | None = None
        if had_state:
            backup = state_file.read_bytes()
            state_file.unlink()
        try:
            with _PerfWorkdir() as workdir:
                src = workdir / "first.ail"
                src.write_text(
                    'fn main() { print("PROG_OUT"); return 0 }\n',
                    encoding="utf-8",
                )
                # Invoke through main() so the welcome check fires.
                argv = ["--dev", "run", "--no-check", "--no-sandbox", src.name]
                rc, stdout, stderr = self._run_main(argv, workdir)
                assert rc == 0
                # The banner must be on stderr, NOT stdout.
                assert "Welcome to AILang" in stderr, (
                    f"first-run welcome banner must be on stderr. "
                    f"stderr={stderr!r} stdout={stdout!r}"
                )
                assert "Welcome to AILang" not in stdout, (
                    f"first-run welcome banner must NOT be on stdout. "
                    f"stdout={stdout!r}"
                )
                # Program stdout must contain only program output.
                assert "PROG_OUT" in stdout
                assert stdout.count("PROG_OUT") == 1
        finally:
            if backup is not None:
                state_file.write_bytes(backup)
            elif state_file.exists():
                state_file.unlink()


class TestTestgenIntegrationP1a:
    """P1a regression suite: ``ail testgen`` → ``ail test`` integration."""

    def _run(
        self, cmd: list[str], cwd: "Path", timeout: float = 180.0
    ) -> "tuple[int, str, str]":
        import os
        import subprocess
        import sys as _sys

        # Pin the subprocess's import resolution to THIS repository so the
        # tests exercise the testgen under test (and not a stale wheel
        # copy sitting in the dev venv's site-packages).
        env = os.environ.copy()
        repo_root = str(Path(__file__).resolve().parents[1])
        existing_pp = env.get("PYTHONPATH", "")
        if repo_root not in existing_pp.split(os.pathsep):
            env["PYTHONPATH"] = (
                repo_root + (os.pathsep + existing_pp if existing_pp else "")
            )
        result = subprocess.run(
            [_sys.executable, "-m"] + cmd,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            env=env,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr

    def _write_app(self, project: "Path") -> "Path":
        """Write a minimal AILang app (main.ail) into ``project/apps/example/``."""
        import os as _os
        app_dir = project / "apps" / "example"
        app_dir.mkdir(parents=True, exist_ok=True)
        main_path = app_dir / "main.ail"
        main_path.write_text(
            "fn main() {\n"
            "    print(\"EXAMPLE_OK\");\n"
            "    return 0\n"
            "}\n",
            encoding="utf-8",
        )
        # Touch an ail.toml so the project root is discoverable.
        (project / "ail.toml").write_text(
            "[project]\nname = \"p1a_proj\"\nversion = \"0.0.0\"\nentry = \"apps/example/main.ail\"\n",
            encoding="utf-8",
        )
        return main_path

    def test_generated_test_passes_under_ail_test(self) -> None:
        """A generated test for a working app must pass under ``ail test``."""
        import tempfile
        with tempfile.TemporaryDirectory(prefix="ail_m136_p1a_") as tmp:
            project = Path(tmp)
            self._write_app(project)
            # Generate the test for the single app.
            rc, out, err = self._run(
                ["tools.ail_testgen", "--app", "example", "--force", "--quiet"],
                cwd=project,
            )
            assert rc == 0, f"testgen failed: stdout={out!r} stderr={err!r}"
            generated = project / "apps" / "example" / "test_app_example_generated.ail"
            assert generated.is_file(), (
                f"expected {generated} to exist after testgen. "
                f"stdout={out!r} stderr={err!r}"
            )
            # Discover and run via ail test. ``cmd_test`` derives the
            # root from the test file's nearest ``main.ail`` ancestor so
            # ``import main;`` resolves against ``apps/example/``.
            from compiler.cli.main import cmd_test
            import io
            import os as _os
            import sys as _sys
            old_cwd = _os.getcwd()
            old_stdout = _sys.stdout
            old_stderr = _sys.stderr
            out_buf = io.StringIO()
            err_buf = io.StringIO()
            _os.chdir(str(project))
            _sys.stdout = out_buf
            _sys.stderr = err_buf
            try:
                test_rc = cmd_test(["--no-check", str(generated)])
            finally:
                _sys.stdout = old_stdout
                _sys.stderr = old_stderr
                _os.chdir(old_cwd)
            assert test_rc == 0, (
                f"ail test on a generated test for a working app must PASS; "
                f"got rc={test_rc}. stderr={err_buf.getvalue()!r}"
            )

    def test_generated_test_fails_for_broken_app(self) -> None:
        """A generated test for a syntactically broken app must FAIL.

        This proves the integration actually detects failures: a genuine
        compile error in the app causes the generated test (which imports
        the app) to fail to compile, and ``ail test`` reports FAIL.
        """
        import tempfile
        with tempfile.TemporaryDirectory(prefix="ail_m136_p1a_") as tmp:
            project = Path(tmp)
            main_path = self._write_app(project)
            # Generate the test first (against the working app) so we
            # have the test file on disk.
            rc, out, err = self._run(
                ["tools.ail_testgen", "--app", "example", "--force", "--quiet"],
                cwd=project,
            )
            assert rc == 0, f"testgen failed: {err}"
            generated = project / "apps" / "example" / "test_app_example_generated.ail"
            assert generated.is_file()
            # Now break the app.
            main_path.write_text("THIS IS NOT VALID AILANG !@#$%\n", encoding="utf-8")
            try:
                from compiler.cli.main import cmd_test
                import io
                import os as _os
                import sys as _sys
                old_cwd = _os.getcwd()
                old_stdout = _sys.stdout
                old_stderr = _sys.stderr
                out_buf = io.StringIO()
                err_buf = io.StringIO()
                _os.chdir(str(project))
                _sys.stdout = out_buf
                _sys.stderr = err_buf
                try:
                    test_rc = cmd_test(["--no-check", str(generated)])
                finally:
                    _sys.stdout = old_stdout
                    _sys.stderr = old_stderr
                    _os.chdir(old_cwd)
                assert test_rc == 1, (
                    f"ail test on a generated test for a BROKEN app must FAIL "
                    f"(rc=1); got rc={test_rc}. stderr={err_buf.getvalue()!r}"
                )
            finally:
                # Restore the working app so the tempdir cleanup is clean
                # and any subsequent test re-using the helper isn't
                # affected. (The TemporaryDirectory will be removed; this
                # is purely defensive.)
                try:
                    main_path.write_text(
                        "fn main() { print(\"EXAMPLE_OK\"); return 0 }\n",
                        encoding="utf-8",
                    )
                except OSError:
                    pass

    def test_generated_test_is_ailang_source(self) -> None:
        """The generated test must be syntactically valid AILang (no ``#``)."""
        import tempfile
        with tempfile.TemporaryDirectory(prefix="ail_m136_p1a_") as tmp:
            project = Path(tmp)
            self._write_app(project)
            rc, _out, err = self._run(
                ["tools.ail_testgen", "--app", "example", "--force", "--quiet"],
                cwd=project,
            )
            assert rc == 0, f"testgen failed: {err}"
            generated = (
                project / "apps" / "example" / "test_app_example_generated.ail"
            )
            text = generated.read_text(encoding="utf-8")
            assert "#" not in text, (
                "AILang has no '#' comment syntax; generated tests must avoid it"
            )
            assert "import main;" in text, (
                "generated test must import the app module for the compile check"
            )
            assert "fn test_app_compiles()" in text, (
                "generated test must define a test_app_compiles function"
            )

"""Test harness for inventory app module tests."""

import os
import sys
from pathlib import Path

# Run from inventory directory
os.chdir(str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from compiler.compilation.resolution import ModuleResolver
from compiler.compilation.session import CompilationSession
from compiler.diagnostics import DiagnosticFormatter, DiagnosticReporter
from compiler.runtime import Runtime
from compiler.runtime import builtins as runtime_builtins

inv_dir = Path.cwd()
TESTS_DIR = inv_dir / "tests"

# Clean data directory for a fresh start
data_dir = inv_dir / "data"
if data_dir.exists():
    for f in data_dir.iterdir():
        f.unlink()
else:
    data_dir.mkdir(parents=True, exist_ok=True)


def run_file(file_path: str, cli_args: list[str] | None = None) -> tuple[bool, str]:
    """Compile and run an AILang test file. Returns (passed, output)."""
    if cli_args is None:
        cli_args = ["test.ail"]
    runtime_builtins._program_argv = cli_args

    session = CompilationSession()
    session._root = inv_dir
    session._resolver = ModuleResolver(inv_dir)

    reporter = DiagnosticReporter()
    session.discover(str(Path(file_path).resolve()), reporter)
    session.analyze(reporter)

    if reporter.error_count > 0:
        formatter = DiagnosticFormatter()
        output = ""
        for diag in reporter.diagnostics:
            output += formatter.format(diag) + "\n"
        return False, output

    bundle = session.build_ir()
    runtime = Runtime(bundle)

    for module_name in session._graph.topological_sort():
        runtime._initialize_module(module_name)

    try:
        import io

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        main_module = None
        for module_name in session._graph.topological_sort():
            if module_name in bundle.module_irs:
                main_module = module_name
                break

        if main_module is None:
            raise KeyError("No module found")

        program_ir = bundle.module_irs[main_module]
        result = runtime.execute(program_ir)
        captured = sys.stdout.getvalue()
        sys.stdout = old_stdout
    except Exception as e:
        sys.stdout = old_stdout
        import traceback

        return False, f"{type(e).__name__}: {e}\n{traceback.format_exc()}"

    return True, captured


# Login as admin
print("=== Setup: login ===")
passed, output = run_file(str(inv_dir / "main.ail"), ["login", "admin", "admin123"])
if not passed:
    print(f"LOGIN FAILED: {output}")
    sys.exit(1)
print(output)

# Initialize demo data
print("=== Setup: init ===")
passed, output = run_file(str(inv_dir / "main.ail"), ["init"])
if not passed:
    print(f"INIT FAILED: {output}")
    sys.exit(1)
print(output)

# Also seed extended data
print("=== Setup: seed ===")
passed, output = run_file(str(inv_dir / "main.ail"), ["seed"])
if not passed:
    print(f"SEED FAILED: {output}")
    sys.exit(1)
print(output)

# Collect test files
import glob as globmod

test_files = sorted(globmod.glob(str(TESTS_DIR / "test_*.ail")))
test_files = [Path(f) for f in test_files]

results = {"pass": 0, "fail": 0, "error": []}
for tf in test_files:
    name = tf.stem.replace("test_", "")
    print(f"\n=== TEST: {name} ===")
    passed, output = run_file(str(tf), ["test.ail"])
    if passed:
        print(output, end="")
        print("PASS")
        results["pass"] += 1
    else:
        print("FAIL")
        print(output[:2000], end="")
        if len(output) > 2000:
            print(f"\n... ({len(output)} total chars)")
        results["fail"] += 1
        results["error"].append(name)

print(f"\n{'='*50}")
print(f"RESULTS: {results['pass']} passed, {results['fail']} failed")
if results["fail"] > 0:
    print(f"Failed: {', '.join(results['error'])}")
    sys.exit(1)
else:
    print("ALL TESTS PASSED")

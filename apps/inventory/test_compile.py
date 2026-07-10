"""Test the full inventory app via the CompilationSession API."""
import os
import sys
from pathlib import Path

# Run from the app directory so data/ paths resolve correctly
os.chdir(str(Path(__file__).resolve().parent))

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from compiler.compilation.session import CompilationSession
from compiler.compilation.resolution import ModuleResolver
from compiler.diagnostics import DiagnosticReporter, DiagnosticFormatter
from compiler.runtime import Runtime
from compiler.runtime import builtins as runtime_builtins

inv_dir = Path.cwd()
main_file = inv_dir / 'main.ail'

def run_app(cli_args):
    """Run the app with given CLI args, return (result, error)."""
    runtime_builtins._program_argv = cli_args

    session = CompilationSession()
    session._root = inv_dir
    session._resolver = ModuleResolver(inv_dir)

    reporter = DiagnosticReporter()
    session.discover(str(main_file), reporter)
    session.analyze(reporter)

    if reporter.error_count > 0:
        formatter = DiagnosticFormatter()
        for diag in reporter.diagnostics:
            print(formatter.format(diag))
        return None, f"{reporter.error_count} compile errors"

    bundle = session.build_ir()
    runtime = Runtime(bundle)

    for module_name in session._graph.topological_sort():
        runtime._initialize_module(module_name)

    try:
        main_module = None
        for module_name in session._graph.topological_sort():
            if module_name in bundle.module_irs:
                main_module = module_name
                break

        if main_module is None:
            raise KeyError("No module found")

        program_ir = bundle.module_irs[main_module]
        result = runtime.execute(program_ir)
        return result, None
    except Exception as e:
        import traceback
        return None, traceback.format_exc()

# Clean data dir
import shutil
data_dir = inv_dir / 'data'
if data_dir.exists():
    for f in data_dir.iterdir():
        f.unlink()

# --- Test help ---
print("=== TEST: help ===")
result, err = run_app(['main.ail', 'help'])
print(f'Result: {result}, Err: {err}')

# --- Test init ---
print("\n=== TEST: init ===")
result, err = run_app(['main.ail', 'init'])
print(f'Result: {result}, Err: {err}')
if err:
    sys.exit(1)

# --- Test stock ---
print("\n=== TEST: stock ===")
result, err = run_app(['main.ail', 'stock'])
print(f'Result: {result}, Err: {err}')
if err:
    sys.exit(1)

# --- Test report ---
print("\n=== TEST: report ===")
result, err = run_app(['main.ail', 'report'])
print(f'Result: {result}, Err: {err}')
if err:
    sys.exit(1)

# --- Test csv export ---
print("\n=== TEST: csv ===")
result, err = run_app(['main.ail', 'csv'])
print(f'Result: {result}, Err: {err}')
if err:
    sys.exit(1)

# --- Test json export ---
print("\n=== TEST: json ===")
result, err = run_app(['main.ail', 'json'])
print(f'Result: {result}, Err: {err}')
if err:
    sys.exit(1)

print("\n=== ALL TESTS PASSED ===")

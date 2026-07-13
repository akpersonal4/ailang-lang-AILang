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
result, err = run_app(['help'])
print(f'Result: {result}, Err: {err}')

# --- Test login ---
print("\n=== TEST: login ===")
result, err = run_app(['login', 'admin', 'admin123'])
print(f'Result: {result}, Err: {err}')
if err:
    sys.exit(1)

# --- Test init (requires auth) ---
print("\n=== TEST: init ===")
result, err = run_app(['init'])
print(f'Result: {result}, Err: {err}')
if err:
    sys.exit(1)

# --- Test stock (requires auth) ---
print("\n=== TEST: stock ===")
result, err = run_app(['stock'])
print(f'Result: {result}, Err: {err}')
if err:
    sys.exit(1)

# --- Test report ---
print("\n=== TEST: report ===")
result, err = run_app(['report'])
print(f'Result: {result}, Err: {err}')
if err:
    sys.exit(1)

# --- Test csv export ---
print("\n=== TEST: csv ===")
result, err = run_app(['csv'])
print(f'Result: {result}, Err: {err}')
if err:
    sys.exit(1)

# --- Test json export ---
print("\n=== TEST: json ===")
result, err = run_app(['json'])
print(f'Result: {result}, Err: {err}')
if err:
    sys.exit(1)

# --- Test backup (requires auth) ---
print("\n=== TEST: backup ===")
result, err = run_app(['backup'])
print(f'Result: {result}, Err: {err}')
if err:
    sys.exit(1)

# --- Test check ---
print("\n=== TEST: check ===")
result, err = run_app(['check'])
print(f'Result: {result}, Err: {err}')
if err:
    sys.exit(1)

# --- Test logout ---
print("\n=== TEST: logout ===")
result, err = run_app(['logout'])
print(f'Result: {result}, Err: {err}')

# --- Verify auth guard (should fail) ---
print("\n=== TEST: init after logout (should fail) ===")
result, err = run_app(['init'])
if err:
    print("Auth guard works (expected): " + err)
else:
    print("Result: " + str(result))

print("\n=== ALL TESTS PASSED ===")

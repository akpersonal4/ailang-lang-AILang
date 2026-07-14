"""Test runner for AILang workflow engine tests — uses compiler API directly."""
import os
import sys
from pathlib import Path

os.chdir(str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from compiler.compilation.session import CompilationSession
from compiler.compilation.resolution import ModuleResolver
from compiler.diagnostics import DiagnosticReporter, DiagnosticFormatter
from compiler.runtime import Runtime
from compiler.runtime import builtins as runtime_builtins

app_dir = Path.cwd()
TESTS_DIR = app_dir / 'tests'

data_dir = app_dir / 'data'
if data_dir.exists():
    for f in data_dir.iterdir():
        if f.suffix == '.json':
            f.unlink()
else:
    data_dir.mkdir(parents=True, exist_ok=True)


def run_file(file_path: str, cli_args: list[str] | None = None) -> tuple[bool, str]:
    if cli_args is None:
        cli_args = ['test.ail']
    runtime_builtins._program_argv = cli_args

    session = CompilationSession()
    session._root = app_dir
    session._resolver = ModuleResolver(app_dir)

    reporter = DiagnosticReporter()
    session.discover(str(Path(file_path).resolve()), reporter)
    session.analyze(reporter)

    if reporter.error_count > 0:
        formatter = DiagnosticFormatter()
        output = ''
        for diag in reporter.diagnostics:
            output += formatter.format(diag) + '\n'
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


import glob as globmod
test_files = sorted(globmod.glob(str(TESTS_DIR / 'test_*.ail')))
test_files = [Path(f) for f in test_files]

if not test_files:
    print("No test_*.ail files found")
    sys.exit(1)

results = {'pass': 0, 'fail': 0, 'error': []}
for tf in test_files:
    name = tf.stem
    print(f"\n=== TEST: {name} ===")
    passed, output = run_file(str(tf), ['test.ail'])
    if passed:
        print(output, end='')
        if "FAIL" in output:
            results['fail'] += 1
            results['error'].append(name)
        else:
            print("PASS")
            results['pass'] += 1
    else:
        print(f"FAIL (compile/runtime error)")
        print(output[:2000], end='')
        results['fail'] += 1
        results['error'].append(name)

print(f"\n{'='*50}")
print(f"RESULTS: {results['pass']} passed, {results['fail']} failed")
if results['fail'] > 0:
    print(f"Failed: {', '.join(results['error'])}")
    sys.exit(1)
else:
    print("ALL TESTS PASSED")

"""Run a single AILang test file and print output."""
import os, sys
from pathlib import Path

os.chdir(str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from compiler.compilation.session import CompilationSession
from compiler.compilation.resolution import ModuleResolver
from compiler.diagnostics import DiagnosticReporter, DiagnosticFormatter
from compiler.runtime import Runtime
from compiler.runtime import builtins as runtime_builtins

test_path = sys.argv[1]
inv_dir = Path.cwd()
runtime_builtins._program_argv = ['test.ail']

session = CompilationSession()
session._root = inv_dir
session._resolver = ModuleResolver(inv_dir)
reporter = DiagnosticReporter()
session.discover(str(Path(test_path).resolve()), reporter)
session.analyze(reporter)

if reporter.error_count > 0:
    formatter = DiagnosticFormatter()
    for diag in reporter.diagnostics:
        print(formatter.format(diag))
    sys.exit(1)

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
    program_ir = bundle.module_irs[main_module]
    runtime.execute(program_ir)
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)

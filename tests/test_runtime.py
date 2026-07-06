from contextlib import redirect_stdout
from io import StringIO

from compiler.ast.builder import ASTBuilder
from compiler.ast.nodes import ProgramNode
from compiler.diagnostics import DiagnosticReporter
from compiler.ir import IRBuilder
from compiler.ir.nodes import ProgramIR
from compiler.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.semantic.symbol_table import SymbolTable
from compiler.types.checker import TypeChecker


def _build_ir(source: str) -> ProgramIR:
    lexer = Lexer()
    parser = Parser(lexer.tokenize(source))
    cst = parser.parse_program()
    ast = ASTBuilder().build(cst)
    assert isinstance(ast, ProgramNode)
    reporter = DiagnosticReporter()
    symbol_table = SymbolTable(reporter)
    SemanticAnalyzer(symbol_table).analyze(ast)
    TypeChecker(symbol_table, reporter).check(ast)
    return IRBuilder().build(ast)


def test_runtime_executes_literal_and_variable() -> None:
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir("let x = 10;")
    result = runtime.execute(ir)

    assert result == 10


def test_runtime_executes_binary_expression() -> None:
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir("let x = 2 + 3;")
    result = runtime.execute(ir)

    assert result == 5


def test_runtime_executes_if_statement() -> None:
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir("fn main() { let x = 1; if (x > 0) { x = 2; } return x; }")
    result = runtime.execute(ir)

    assert result == 2


def test_runtime_executes_function_arguments_and_returns() -> None:
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir("fn add(a, b) { return a + b; } fn main() { return add(10, 20); }")
    result = runtime.execute(ir)

    assert result == 30


def test_runtime_supports_nested_function_calls() -> None:
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir(
        "fn square(x) { return x * x; } fn main() { let y = 3; return square(y + 1); }"
    )
    result = runtime.execute(ir)

    assert result == 16


def test_runtime_supports_multiple_functions_and_local_scope() -> None:
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir(
        "fn add(a, b) { return a + b; } "
        "fn main() { let x = 2; let y = 3; return add(x, y); }"
    )
    result = runtime.execute(ir)

    assert result == 5


def test_runtime_supports_recursive_calls() -> None:
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir(
        "fn recurse(x) { if (x == 0) { return 0; } "
        "return recurse(x - 1); } fn main() { return recurse(3); }"
    )
    result = runtime.execute(ir)

    assert result == 0


def test_runtime_supports_variable_shadowing_in_nested_scope() -> None:
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir(
        "fn main() { let x = 1; if (1 == 1) { let x = 2; return x; } " "return x; }"
    )
    result = runtime.execute(ir)

    assert result == 2


def test_runtime_supports_builtin_print() -> None:
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir("fn main() { print(42); return 7; }")
    output = StringIO()
    with redirect_stdout(output):
        result = runtime.execute(ir)

    assert result == 7
    assert output.getvalue() == "42\n"


def test_environment_resolves_parent_values_and_assignments() -> None:
    from compiler.runtime.environment import Environment

    parent = Environment()
    parent.define("x", 1)
    child = Environment(parent=parent)

    assert child.resolve("x") == 1

    child.assign("x", 2)

    assert parent.resolve("x") == 2


def test_stack_frame_tracks_return_value() -> None:
    from compiler.runtime.stack_frame import StackFrame

    frame = StackFrame(function_name="main")
    frame.set_return_value(9)

    assert frame.return_value == 9


# -------------------------------------------------------------------------
# Regression tests for RUNTIME-001
# -------------------------------------------------------------------------
# Bug: _set_local used Environment.assign() (traverses parent chain) for
# 'let' declarations, causing variables to leak to the global environment.
# Two functions using 'let result = ...' would overwrite each other.
#
# Fix: Split into _define_local (uses define(), for 'let') and
# _assign_local (uses assign(), for '=' reassignment).
# -------------------------------------------------------------------------


def test_runtime_cross_function_isolation() -> None:
    """Verify 'let' declarations in different functions are independent.

    Two functions each declare 'let x = ...' with different integer values.
    Calling them in sequence must not corrupt the first function's value.
    """
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir(
        "fn a() {\n"
        "  let x = 10;\n"
        "  return x\n"
        "}\n"
        "fn b() {\n"
        "  let x = 20;\n"
        "  return x\n"
        "}\n"
        "fn main() {\n"
        "  let v1 = a();\n"
        "  let v2 = b();\n"
        "  if (v1 == 10 && v2 == 20) { return 1 }\n"
        "  return 0\n"
        "}"
    )
    assert runtime.execute(ir) == 1


def test_runtime_same_name_three_functions() -> None:
    """Verify three functions using 'let data = ...' don't interfere."""
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir(
        "fn f1() { let data = 1; return data }\n"
        "fn f2() { let data = 2; return data }\n"
        "fn f3() { let data = 3; return data }\n"
        "fn main() {\n"
        "  let a = f1();\n"
        "  let b = f2();\n"
        "  let c = f3();\n"
        "  if (a == 1 && b == 2 && c == 3) { return 1 }\n"
        "  return 0\n"
        "}"
    )
    assert runtime.execute(ir) == 1


def test_runtime_recursive_let_isolation() -> None:
    """Verify each recursive call has independent 'let' bindings."""
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir(
        "fn sum_to(n, acc) {\n"
        "  if (n <= 0) { return acc }\n"
        "  let tmp = n + acc;\n"
        "  return sum_to(n - 1, tmp)\n"
        "}\n"
        "fn main() { return sum_to(5, 0) }"
    )
    assert runtime.execute(ir) == 15


def test_runtime_repeated_call_returns_same_value() -> None:
    """Verify calling a function twice returns the same value.

    Regression test for RUNTIME-001: if 'let result' in function A leaks
    to global, calling function B (which also uses 'let result') between
    two calls to A would corrupt A's variable. With the fix, each call
    creates a fresh local binding.
    """
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir(
        "fn make_a() {\n"
        "  let result = 42;\n"
        "  return result\n"
        "}\n"
        "fn make_b() {\n"
        "  let result = 99;\n"
        "  return result\n"
        "}\n"
        "fn main() {\n"
        "  let first = make_a();\n"
        "  let _ = make_b();\n"
        "  let second = make_a();\n"
        "  if (first == 42 && second == 42) { return 1 }\n"
        "  return 0\n"
        "}"
    )
    assert runtime.execute(ir) == 1


def test_runtime_independent_scope_chains() -> None:
    """Verify deeply nested calls with same variable names don't leak.

    Three levels of function calls, each using 'let val = ...'.
    """
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir(
        "fn inner() { let val = 3; return val }\n"
        "fn middle() { let val = 2; let i = inner(); return val + i }\n"
        "fn outer() { let val = 1; let m = middle(); return val + m }\n"
        "fn main() { return outer() }"
    )
    assert runtime.execute(ir) == 6  # 1 + (2 + 3)


def test_runtime_assignment_uses_correct_scope() -> None:
    """Verify '=' reassignment finds the variable in the correct scope.

    With the fix, 'let x = 1' creates a local 'x', and 'x = 999' must
    update that local (not the global). This test verifies that
    AssignmentIR still uses assign() which traverses the scope chain.
    """
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir("fn main() {\n" "  let x = 1;\n" "  x = 999;\n" "  return x\n" "}")
    assert runtime.execute(ir) == 999


def test_runtime_assignment_finds_outer_variable() -> None:
    """Verify '=' reassignment traverses to outer scope if not local.

    If a variable is not declared in the current scope but exists in an
    outer scope, '=' assignment should update the outer variable.
    """
    from compiler.runtime import Runtime

    runtime = Runtime()
    ir = _build_ir(
        "fn main() {\n"
        "  let x = 1;\n"
        "  if (1 == 1) {\n"
        "    x = 888;\n"
        "  }\n"
        "  return x\n"
        "}"
    )
    assert runtime.execute(ir) == 888

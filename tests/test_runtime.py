from contextlib import redirect_stdout
from io import StringIO

from compiler.ast.builder import ASTBuilder
from compiler.diagnostics import DiagnosticReporter
from compiler.ir import IRBuilder
from compiler.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.semantic.symbol_table import SymbolTable
from compiler.types.checker import TypeChecker


def _build_ir(source: str):
    lexer = Lexer()
    parser = Parser(lexer.tokenize(source))
    cst = parser.parse_program()
    ast = ASTBuilder().build(cst)
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

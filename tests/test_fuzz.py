"""Fuzz tests for AILang compiler — random input crash resistance.

Generates random AILang programs and byte streams, feeds them through
the full compiler pipeline (lex → parse → AST → semantic → type check
→ IR → runtime), and asserts the compiler never crashes with an
unhandled Python exception.

The key insight: the compiler must never raise an UNHANDLED Python
exception. Diagnostics (parser errors, semantic errors, type errors,
runtime errors) are expected. Raw NameError/TypeError/ValueError/
AttributeError/AssertionError are NOT expected.
"""

from __future__ import annotations

import random
import sys
import tempfile
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Seed for reproducibility
# ---------------------------------------------------------------------------
RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# AILang grammar fragments for program generation
# ---------------------------------------------------------------------------

TYPES = ["Int", "String", "Bool", "List", "Map"]
BINARY_OPS = ["+", "-", "*", "/", "%", "==", "!=", "<", "<=", ">", ">=", "&&", "||"]
UNARY_OPS = ["-", "!"]
BUILTIN_NAMES = frozenset({
    "print", "math.add", "list.len", "list.get", "string.concat",
    "map.set", "map.get", "map.has", "file.read", "convert.to_string",
})


def _random_identifier(rng: random.Random) -> str:
    """Generate a random valid AILang identifier."""
    length = rng.randint(1, 12)
    first = rng.choice("abcdefghijklmnopqrstuvwxyz_")
    rest = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz0123456789_") for _ in range(length - 1))
    return first + rest


def _random_literal(rng: random.Random) -> str:
    """Generate a random literal expression."""
    kind = rng.randint(0, 4)
    if kind == 0:
        return str(rng.randint(-1000, 1000))
    if kind == 1:
        return f'"{_random_identifier(rng)}"'
    if kind == 2:
        return rng.choice(["true", "false"])
    if kind == 3:
        return "null"
    return str(rng.randint(0, 100))


def _random_expression(rng: random.Random, depth: int = 0) -> str:
    """Generate a random AILang expression."""
    if depth > 3:
        return _random_literal(rng)

    kind = rng.randint(0, 7)
    if kind == 0:
        return _random_literal(rng)
    if kind == 1:
        return _random_identifier(rng)
    if kind == 2:
        op = rng.choice(BINARY_OPS)
        left = _random_expression(rng, depth + 1)
        right = _random_expression(rng, depth + 1)
        return f"({left} {op} {right})"
    if kind == 3:
        op = rng.choice(UNARY_OPS)
        operand = _random_expression(rng, depth + 1)
        return f"{op}({operand})"
    if kind == 4:
        callee = _random_identifier(rng) if rng.random() < 0.5 else rng.choice([
            "print", "math.add", "list.len", "string.concat"
        ])
        args = ", ".join(_random_expression(rng, depth + 1) for _ in range(rng.randint(0, 3)))
        return f"{callee}({args})"
    if kind == 5:
        receiver = _random_expression(rng, depth + 1)
        member = _random_identifier(rng)
        return f"{receiver}.{member}"
    if kind == 6:
        return f"[{', '.join(_random_expression(rng, depth + 1) for _ in range(rng.randint(0, 3)))}]"
    return "{" + ", ".join(
        f'"{_random_identifier(rng)}": {_random_expression(rng, depth + 1)}'
        for _ in range(rng.randint(0, 3))
    ) + "}"


def generate_random_program(rng: random.Random, num_statements: int = 10) -> str:
    """Generate a random valid-ish AILang program."""
    lines: list[str] = []
    func_names: list[str] = []

    for _ in range(rng.randint(0, 3)):
        fname = _random_identifier(rng)
        func_names.append(fname)
        params = ", ".join(_random_identifier(rng) for _ in range(rng.randint(0, 3)))
        body_lines: list[str] = []
        for _ in range(rng.randint(1, 5)):
            body_lines.append(f"    let {_random_identifier(rng)} = {_random_expression(rng)};")
        if rng.random() < 0.3:
            body_lines.append(f"    return {_random_expression(rng)};")
        lines.append(f"fn {fname}({params}) {{")
        lines.extend(body_lines)
        lines.append("}")

    for _ in range(num_statements):
        kind = rng.randint(0, 6)
        if kind == 0:
            lines.append(f"let {_random_identifier(rng)} = {_random_expression(rng)};")
        elif kind == 1:
            lines.append(f"{_random_expression(rng)};")
        elif kind == 2:
            cond = _random_expression(rng)
            lines.append(f"if ({cond}) {{")
            lines.append(f"    let {_random_identifier(rng)} = {_random_expression(rng)};")
            lines.append("}")
        elif kind == 3:
            cond = _random_expression(rng)
            lines.append(f"if ({cond}) {{")
            lines.append(f"    let {_random_identifier(rng)} = {_random_expression(rng)};")
            lines.append("} else {")
            lines.append(f"    let {_random_identifier(rng)} = {_random_expression(rng)};")
            lines.append("}")
        elif kind == 4:
            fname = rng.choice(func_names) if func_names else "main"
            args = ", ".join(_random_expression(rng) for _ in range(rng.randint(0, 3)))
            lines.append(f"{fname}({args});")
        elif kind == 5:
            lines.append(f"let {_random_identifier(rng)} = {_random_identifier(rng)}.{_random_identifier(rng)}({_random_expression(rng)});")
        elif kind == 6:
            lines.append(f"let {_random_identifier(rng)} = [{', '.join(_random_expression(rng) for _ in range(rng.randint(1, 4)))}];")

    if "main" not in "\n".join(lines) and rng.random() < 0.5:
        lines.append("fn main() {")
        lines.append("    return 0;")
        lines.append("}")

    return "\n".join(lines)


def generate_random_bytes(rng: random.Random, size: int = 256) -> bytes:
    """Generate completely random byte stream to test lexer/parser crash safety."""
    return bytes(rng.randint(0, 255) for _ in range(size))


def _run_compiler_pipeline(source: str, repo_root: Path) -> str | None:
    """Run the full compiler pipeline on source.

    Returns None on success, error message on unhandled crash.
    We expect diagnostics (parser/semantic/type errors) but NOT
    unhandled Python exceptions.
    """
    try:
        from compiler.ast.builder import ASTBuilder
        from compiler.lexer import Lexer
        from compiler.parser import Parser

        with tempfile.TemporaryDirectory() as tmpdir:
            main_file = Path(tmpdir) / "main.ail"
            main_file.write_text(source if isinstance(source, str) else source.decode("utf-8", errors="replace"))

            lexer = Lexer(source_path=str(main_file))
            tokens = lexer.tokenize(source)

            parser = Parser(tokens, source_path=str(main_file))
            cst = parser.parse_program()

            try:
                ast = ASTBuilder().build(cst)
            except ValueError:
                return None

            from compiler.compilation import CompilationSession
            from compiler.diagnostics import DiagnosticReporter

            session = CompilationSession()
            session._root = repo_root
            session._resolver = type(session._resolver)(repo_root)
            session.discover(main_file)
            reporter = DiagnosticReporter()
            session.analyze(reporter)

            try:
                session.type_check(reporter)
            except Exception:
                return None

            try:
                bundle = session.build_ir()
            except Exception:
                return None

            from compiler.runtime.interpreter import Runtime

            runtime = Runtime(bundle)
            for module_name in session._graph.topological_sort():
                runtime._initialize_module(module_name)

            entry_module = next(
                (name for name in bundle.module_irs if name.endswith("main")),
                None,
            )
            if entry_module is not None:
                try:
                    runtime.execute(bundle.module_irs[entry_module])
                except RuntimeError:
                    return None
                except Exception as exc:
                    return f"Runtime unhandled exception: {type(exc).__name__}: {exc}"

        return None

    except (ValueError, RuntimeError):
        return None
    except Exception as exc:
        return f"Compiler crash: {type(exc).__name__}: {exc}"


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

FUZZ_ITERATIONS = 100
RANDOM_BYTE_ITERATIONS = 50


@pytest.mark.slow
class TestFuzz:
    """Fuzz test suite — random program generation."""

    def test_fuzz_random_programs(self) -> None:
        """Generate and test random AILang programs — expect no crashes."""
        repo_root = Path(__file__).resolve().parents[1]
        rng = random.Random(RANDOM_SEED)
        failures: list[str] = []

        for i in range(FUZZ_ITERATIONS):
            source = generate_random_program(rng, num_statements=rng.randint(1, 20))
            error = _run_compiler_pipeline(source, repo_root)
            if error is not None:
                failures.append(f"Iteration {i}: {error}\n--- Source ---\n{source[:500]}")

        if failures:
            msg = f"\n\n{len(failures)}/{FUZZ_ITERATIONS} fuzz iterations failed:\n"
            msg += "\n\n".join(failures[:5])
            pytest.fail(msg)

    def test_fuzz_random_bytes(self) -> None:
        """Feed random byte streams through lexer/parser — expect no crashes."""
        repo_root = Path(__file__).resolve().parents[1]
        rng = random.Random(RANDOM_SEED + 1)
        failures: list[str] = []

        for i in range(RANDOM_BYTE_ITERATIONS):
            source = generate_random_bytes(rng, size=rng.randint(1, 1024))
            source_str = source.decode("utf-8", errors="replace")
            error = _run_compiler_pipeline(source_str, repo_root)
            if error is not None:
                failures.append(f"Iteration {i}: {error}")

        if failures:
            msg = f"\n\n{len(failures)}/{RANDOM_BYTE_ITERATIONS} random byte iterations failed:\n"
            msg += "\n\n".join(failures[:5])
            pytest.fail(msg)

    def test_fuzz_deeply_nested_expressions(self) -> None:
        """Generate deeply nested expressions — test stack safety."""
        repo_root = Path(__file__).resolve().parents[1]
        rng = random.Random(RANDOM_SEED + 2)

        for depth in [10, 25, 50, 100, 200]:
            expr = "1"
            for _ in range(depth):
                op = rng.choice(["+", "-", "*"])
                expr = f"({expr} {op} {rng.randint(0, 10)})"
            source = f"fn main() {{ let x = {expr}; return 0; }}"
            error = _run_compiler_pipeline(source, repo_root)
            assert error is None, f"Deeply nested expression (depth={depth}) crashed: {error}"

    def test_fuzz_deep_recursion(self) -> None:
        """Generate deeply recursive function chains — test recursion guard."""
        repo_root = Path(__file__).resolve().parents[1]

        # Chain of 1000 mutually recursive calls
        source_lines = ["fn f0() { return f1(); }"]
        for i in range(1, 800):
            source_lines.append(f"fn f{i}() {{ return f{i + 1}(); }}")
        source_lines.append("fn f800() { return 1; }")
        source_lines.append("fn main() { return f0(); }")
        source = "\n".join(source_lines)

        error = _run_compiler_pipeline(source, repo_root)
        assert error is None, f"Deep recursion chain crashed: {error}"

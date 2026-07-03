"""Tests for import declarations in AST and parser."""

from compiler.ast.builder import ASTBuilder
from compiler.ast.nodes import ImportDeclarationNode, ProgramNode
from compiler.lexer import Lexer
from compiler.parser import Parser


def _build(source: str) -> ProgramNode:
    lexer = Lexer()
    parser = Parser(lexer.tokenize(source))
    cst = parser.parse_program()
    ast = ASTBuilder().build(cst)
    assert isinstance(ast, ProgramNode)
    return ast


def test_ast_builds_simple_import() -> None:
    ast = _build("import math;")
    imp = ast.children[0]
    assert isinstance(imp, ImportDeclarationNode)
    assert imp.module_path == ("math",)
    assert imp.alias is None


def test_ast_builds_alias_import() -> None:
    ast = _build("import math as m;")
    imp = ast.children[0]
    assert isinstance(imp, ImportDeclarationNode)
    assert imp.module_path == ("math",)
    assert imp.alias == "m"


def test_ast_builds_nested_module_import() -> None:
    ast = _build("import io.file;")
    imp = ast.children[0]
    assert isinstance(imp, ImportDeclarationNode)
    assert imp.module_path == ("io", "file")
    assert imp.alias is None


def test_ast_builds_nested_module_with_alias() -> None:
    ast = _build("import io.file as file;")
    imp = ast.children[0]
    assert isinstance(imp, ImportDeclarationNode)
    assert imp.module_path == ("io", "file")
    assert imp.alias == "file"

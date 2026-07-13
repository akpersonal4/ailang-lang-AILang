"""Deterministic AILang source code formatter.

Produces a single canonical formatting style with no configuration.
Operates on the AST to validate syntax, then reformats source text,
preserving comments by extracting them from the original source.
"""

from __future__ import annotations

from compiler.ast.builder import ASTBuilder
from compiler.ast.nodes import (
    ASTNode,
    BinaryExpressionNode,
    BlockNode,
    BooleanLiteralNode,
    CallExpressionNode,
    ExpressionStatementNode,
    FunctionDeclarationNode,
    IdentifierNode,
    IfStatementNode,
    ImportDeclarationNode,
    MemberAccessNode,
    NumberLiteralNode,
    ProgramNode,
    ReturnStatementNode,
    StringLiteralNode,
    UnaryExpressionNode,
    VariableDeclarationNode,
)
from compiler.lexer import Lexer
from compiler.parser.nodes import CSTNode
from compiler.parser.parser import Parser

# =============================================================================
# Public API
# =============================================================================


def format_source(source: str) -> str:
    """Parse and format an AILang source string.

    Returns the formatted source.
    Raises ValueError on parse errors.
    """
    ast = _parse_to_ast(source)
    formatter = _Formatter(source, ast)
    return formatter.format()


def format_check(source: str) -> bool:
    """Return True if source is already formatted."""
    formatted = format_source(source)
    return source == formatted


def _parse_to_ast(source: str) -> ProgramNode:
    """Parse source to AST, tolerating missing semicolons.

    Missing semicolons are the most common "syntax error" in handwritten
    AILang code.  The parser still produces a valid CST (and therefore a
    valid AST) when they are absent, so we proceed and let the formatter
    reinsert them in the output.  Other syntax errors (e.g. ``let x = ;``)
    still raise ``ValueError``.
    """
    from compiler.diagnostics import DiagnosticReporter

    reporter = DiagnosticReporter()
    lexer = Lexer(reporter)
    tokens = lexer.tokenize(source)
    parser = Parser(tokens, reporter)
    cst: CSTNode = parser.parse_program()

    # Filter out "Expected SEMICOLON" — the parser recovers fully from
    # missing semicolons and produces a valid CST that the AST builder
    # can process.
    real_errors = [
        d for d in reporter.diagnostics
        if "Expected SEMICOLON" not in d.message
    ]
    if real_errors:
        msgs = [d.message for d in real_errors]
        raise ValueError("Syntax errors: " + "; ".join(msgs))

    builder = ASTBuilder()
    try:
        ast = builder.build(cst)
    except (ValueError, AssertionError, IndexError, AttributeError) as e:
        msgs = [
            d.message for d in reporter.diagnostics
            if "Expected SEMICOLON" not in d.message
        ]
        if not msgs:
            msgs = [str(e)]
        raise ValueError("Syntax errors: " + "; ".join(msgs)) from e

    if not isinstance(ast, ProgramNode):
        raise ValueError("Expected ProgramNode")
    return ast


# =============================================================================
# Comment extraction
# =============================================================================


def _line_from_offset(source: str, offset: int) -> int:
    """Return 0-indexed line number for a character offset."""
    return source[:offset].count("\n") if offset else 0


# =============================================================================
# Formatter
# =============================================================================


class _Formatter:
    """Walk the AST and emit formatted source text."""

    INDENT = "    "

    def __init__(self, source: str, ast: ProgramNode) -> None:
        self.source = source
        self.source_lines = source.split("\n") if source else []
        self.ast = ast
        self._lines: list[str] = []
        self._indent = 0
        self._last_source_line: int = -1

    def format(self) -> str:
        self._format_program(self.ast)
        result = "\n".join(self._lines)
        if not result.endswith("\n"):
            result += "\n"
        return result

    # ------------------------------------------------------------------
    # Indentation helpers
    # ------------------------------------------------------------------

    def _push(self) -> None:
        self._indent += 1

    def _pop(self) -> None:
        self._indent -= 1

    def _cur_indent(self) -> str:
        return self.INDENT * self._indent

    def _emit(self, text: str = "") -> None:
        self._lines.append(f"{self._cur_indent()}{text}")

    def _blank(self) -> None:
        self._lines.append("")

    # ------------------------------------------------------------------
    # Comment helpers
    # ------------------------------------------------------------------

    def _comments_between(
        self, start_line: int, end_line: int
    ) -> list[tuple[int, str]]:
        """Return comment lines between start_line and end_line (exclusive)."""
        found: list[tuple[int, str]] = []
        for lineno, line in enumerate(self.source_lines):
            if lineno > start_line and lineno < end_line:
                stripped = line.strip()
                if stripped.startswith("//"):
                    found.append((lineno, stripped[2:].strip()))
        return found

    def _find_comment_start(self, line: str) -> int:
        """Return index of // that is not inside a string literal, or -1."""
        in_string = False
        i = 0
        while i < len(line):
            c = line[i]
            if c == "\\" and in_string:
                i += 1  # skip escaped character inside string
            elif c == '"':
                in_string = not in_string
            elif c == "/" and i + 1 < len(line) and line[i + 1] == "/":
                if not in_string:
                    return i
                i += 1  # skip second /
            i += 1
        return -1

    def _inline_comment(self, source_line: int) -> str | None:
        """Return inline comment text for a given source line, or None."""
        if 0 <= source_line < len(self.source_lines):
            line = self.source_lines[source_line]
            idx = self._find_comment_start(line)
            if idx >= 0:
                text = line[idx + 2 :].strip()
                if text:
                    return text
        return None

    def _find_source_line(self, code_text: str, approx_start: int = 0) -> int:
        """Search source for a code line to find its line number."""
        clean = code_text.rstrip(";{}").replace(" ", "")
        for lineno, line in enumerate(self.source_lines):
            if lineno < approx_start:
                continue
            if clean in line.replace(" ", ""):
                return lineno
        return approx_start

    def _emit_with_comments(self, code_text: str, source_start: int | None) -> None:
        """Emit a code line, prepending any preceding comment lines first."""
        if source_start is not None:
            node_line = _line_from_offset(self.source, source_start)
        else:
            node_line = self._find_source_line(code_text, self._last_source_line + 1)
        comments = self._comments_between(self._last_source_line, node_line)
        for _, comment_text in comments:
            self._emit(f"// {comment_text}")
        inline = self._inline_comment(node_line)
        if inline:
            self._emit(f"{code_text}  // {inline}")
        else:
            self._emit(code_text)
        self._last_source_line = node_line

    # ------------------------------------------------------------------
    # Program
    # ------------------------------------------------------------------

    def _format_program(self, node: ProgramNode) -> None:
        children = node.children
        last_was_function = False
        last_was_import = False
        before_first_function = True

        for child in children:
            if isinstance(child, ImportDeclarationNode):
                if last_was_function:
                    self._blank()
                self._format_import_declaration(child)
                last_was_function = False
                last_was_import = True
                before_first_function = True

            elif isinstance(child, FunctionDeclarationNode):
                if not before_first_function and last_was_function:
                    self._blank()
                if not before_first_function and not last_was_function:
                    self._blank()
                if last_was_import:
                    self._blank()
                self._format_function_declaration(child)
                last_was_function = True
                last_was_import = False
                before_first_function = False

            elif isinstance(child, VariableDeclarationNode):
                self._blank()
                self._emit_with_comments("", child.start_span)
                self._format_variable_declaration(child)
                last_was_function = False
                last_was_import = False
                before_first_function = False

            else:
                self._blank()
                self._format_node(child)
                last_was_function = False
                last_was_import = False
                before_first_function = False

        # Trailing comments after last AST node, or all comments if no AST nodes
        if children:
            last_end_line = _line_from_offset(self.source, children[-1].end_span or 0)
            comments = self._comments_between(last_end_line, len(self.source_lines))
        else:
            comments = self._comments_between(-1, len(self.source_lines))
        for _, comment_text in comments:
            self._emit(f"// {comment_text}")

    # ------------------------------------------------------------------
    # Declarations
    # ------------------------------------------------------------------

    def _format_import_declaration(self, node: ImportDeclarationNode) -> None:
        path = ".".join(node.module_path)
        if node.alias:
            code = f"import {path} as {node.alias};"
        else:
            code = f"import {path};"
        self._emit_with_comments(code, node.start_span)

    def _format_variable_declaration(self, node: VariableDeclarationNode) -> None:
        name = self._format_expression(node.name)
        init = self._format_expression(node.initializer)
        code = f"let {name} = {init};"
        self._emit_with_comments(code, node.start_span)

    def _format_function_declaration(self, node: FunctionDeclarationNode) -> None:
        name = node.name.name
        parts: list[str] = []
        for p in node.parameters:
            if p.default_value is not None:
                parts.append(
                    f"{p.name} = {self._format_expression(p.default_value)}"
                )
            else:
                parts.append(p.name)
        params = ", ".join(parts)
        header = f"fn {name}({params})"
        self._emit_with_comments(header, node.start_span)
        self._append_brace()
        self._format_block_body(node.body)

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def _format_expression_statement(self, node: ExpressionStatementNode) -> None:
        expr = self._format_expression(node.expression)
        code = f"{expr};"
        self._emit_with_comments(code, node.start_span)

    def _format_return_statement(self, node: ReturnStatementNode) -> None:
        value = self._format_expression(node.value)
        code = f"return {value};"
        self._emit_with_comments(code, node.start_span)

    def _format_if_statement(self, node: IfStatementNode) -> None:
        cond = self._format_expression(node.condition)
        header = f"if ({cond})"
        self._emit_with_comments(header, node.start_span)
        self._append_brace()
        self._format_block_body(node.then_block)

        if node.else_block is not None:
            else_stmts = node.else_block.statements
            if len(else_stmts) == 1 and isinstance(else_stmts[0], IfStatementNode):
                self._lines[-1] += " else "
                self._format_else_if(else_stmts[0])
            else:
                self._lines[-1] += " else {"
                self._push()
                for child in else_stmts:
                    self._format_node(child)
                self._pop()
                self._emit("}")

    def _format_else_if(self, node: IfStatementNode) -> None:
        """Append 'else if (...)' to previous line and continue."""
        cond = self._format_expression(node.condition)
        self._lines[-1] += f"if ({cond})"
        self._append_brace()
        self._format_block_body(node.then_block)

        if node.else_block is not None:
            else_stmts = node.else_block.statements
            if len(else_stmts) == 1 and isinstance(else_stmts[0], IfStatementNode):
                self._lines[-1] += " else "
                self._format_else_if(else_stmts[0])
            else:
                self._lines[-1] += " else {"
                self._push()
                for child in else_stmts:
                    self._format_node(child)
                self._pop()
                self._emit("}")

    # ------------------------------------------------------------------
    # Block helpers
    # ------------------------------------------------------------------

    def _append_brace(self) -> None:
        """Append ' {' to the last emitted line."""
        if self._lines:
            self._lines[-1] += " {"
        else:
            self._emit("{")

    def _format_block_body(self, node: BlockNode) -> None:
        """Format the body of a block (after {, before })."""
        stmts = node.statements
        if not stmts:
            # Empty block: replace "{ {" with "{}"
            if self._lines and self._lines[-1].endswith(" {"):
                self._lines[-1] = self._lines[-1][:-2] + " {}"
            return
        self._push()
        for child in stmts:
            self._format_node(child)
        self._pop()
        self._emit("}")

    # ------------------------------------------------------------------
    # Node dispatch
    # ------------------------------------------------------------------

    def _format_node(self, node: ASTNode) -> None:
        if isinstance(node, FunctionDeclarationNode):
            self._format_function_declaration(node)
        elif isinstance(node, VariableDeclarationNode):
            self._format_variable_declaration(node)
        elif isinstance(node, ExpressionStatementNode):
            self._format_expression_statement(node)
        elif isinstance(node, ReturnStatementNode):
            self._format_return_statement(node)
        elif isinstance(node, IfStatementNode):
            self._format_if_statement(node)
        elif isinstance(node, ImportDeclarationNode):
            self._format_import_declaration(node)
        elif isinstance(node, ProgramNode):
            self._format_program(node)

    # ------------------------------------------------------------------
    # Expression formatters (return string, do not emit lines)
    # ------------------------------------------------------------------

    def _format_expression(
        self, node: ASTNode, parent_prec: int = 0, is_left: bool = False
    ) -> str:
        if isinstance(node, IdentifierNode):
            return node.name
        if isinstance(node, NumberLiteralNode):
            return node.value
        if isinstance(node, StringLiteralNode):
            escaped = (
                node.value.replace("\\", "\\\\")
                .replace('"', '\\"')
                .replace("\n", "\\n")
                .replace("\t", "\\t")
                .replace("\r", "\\r")
            )
            return f'"{escaped}"'
        if isinstance(node, BooleanLiteralNode):
            return "true" if node.value else "false"
        if isinstance(node, BinaryExpressionNode):
            expr = self._format_binary(node)
            node_prec = self._op_precedence(node.operator)
            if parent_prec > 0 and node_prec < parent_prec:
                expr = f"({expr})"
            return expr
        if isinstance(node, UnaryExpressionNode):
            expr = self._format_unary(node)
            if parent_prec > self._op_precedence("*"):
                expr = f"({expr})"
            return expr
        if isinstance(node, CallExpressionNode):
            return self._format_call(node)
        if isinstance(node, MemberAccessNode):
            return self._format_member_access(node)
        if isinstance(node, VariableDeclarationNode):
            name = self._format_expression(node.name)
            init = self._format_expression(node.initializer)
            return f"let {name} = {init}"
        return str(node)

    _PRECEDENCE: dict[str, int] = {
        "=": 1,
        "||": 2,
        "&&": 3,
        "==": 4,
        "!=": 4,
        "<": 5,
        ">": 5,
        "<=": 5,
        ">=": 5,
        "+": 6,
        "-": 6,
        "*": 7,
        "/": 7,
        "%": 7,
    }

    @classmethod
    def _op_precedence(cls, op: str) -> int:
        return cls._PRECEDENCE.get(op, 0)

    def _format_binary(self, node: BinaryExpressionNode) -> str:
        left = self._format_expression(
            node.left, parent_prec=self._op_precedence(node.operator), is_left=True
        )
        right = self._format_expression(
            node.right, parent_prec=self._op_precedence(node.operator), is_left=False
        )
        op = node.operator
        return f"{left} {op} {right}"

    def _format_unary(self, node: UnaryExpressionNode) -> str:
        operand = self._format_expression(node.operand)
        return f"{node.operator}{operand}"

    def _format_call(self, node: CallExpressionNode) -> str:
        callee = self._format_expression(node.callee)
        args = ", ".join(self._format_expression(a) for a in node.arguments)
        return f"{callee}({args})"

    def _format_member_access(self, node: MemberAccessNode) -> str:
        receiver = self._format_expression(node.receiver)
        return f"{receiver}.{node.member.name}"

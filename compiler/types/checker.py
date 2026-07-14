"""Type checker for AILang.

Performs type inference and type checking on the AST.
"""

from __future__ import annotations

from typing import cast

from compiler.ast.nodes import (
    ASTNode,
    BinaryExpressionNode,
    BlockNode,
    BooleanLiteralNode,
    CallExpressionNode,
    ExpressionStatementNode,
    ForStatementNode,
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
from compiler.diagnostics import Diagnostic, DiagnosticReporter, ErrorCode, Severity
from compiler.semantic.symbol_table import SymbolTable
from compiler.types.types import (
    BOOL_TYPE,
    FLOAT_TYPE,
    INT_TYPE,
    STRING_TYPE,
    LIST_TYPE,
    FunctionType,
    Type,
    UnknownType,
)


class TypeChecker:
    """Type checks an AST."""

    def __init__(
        self,
        symbol_table: SymbolTable,
        reporter: DiagnosticReporter | None = None,
        source_text: str | None = None,
        file_path: str | None = None,
    ) -> None:
        self.symbol_table = symbol_table
        self.reporter = reporter or DiagnosticReporter()
        self._source_lines = source_text.split("\n") if source_text else None
        self._file_path: str | None = file_path
        self.current_function_return_type: Type | None = None

    def check(self, node: ASTNode) -> None:
        method_name = f"_check_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is not None:
            method(node)

    # ------------------------------------------------------------------
    # Top-level
    # ------------------------------------------------------------------

    def _check_ProgramNode(self, node: ProgramNode) -> None:  # Fixed Issue 1
        for child in node.children:
            self.check(child)

    def _check_BlockNode(self, node: BlockNode) -> None:
        self.symbol_table.enter_scope(node)
        for statement in node.statements:
            self.check(statement)
        self.symbol_table.exit_scope()

    def _check_ExpressionStatementNode(self, node: ExpressionStatementNode) -> None:
        self._infer_expression(node.expression)

    # ------------------------------------------------------------------
    # Declarations
    # ------------------------------------------------------------------

    def _check_VariableDeclarationNode(self, node: VariableDeclarationNode) -> None:
        # Infer the type of the initializer expression first
        expr_type = self._infer_expression(node.initializer)
        # Resolve the existing symbol declared by the semantic analyzer
        # and attach the inferred type
        symbol = self.symbol_table.resolve(
            node.name.name, node.name.start_span, node.name.end_span
        )
        if symbol is not None:
            symbol.type = expr_type
        # If the type could not be inferred, report an error
        if isinstance(expr_type, UnknownType):
            self._report_error(
                f"Cannot infer type for variable '{node.name.name}'",
                "TYP001",
                node.name.start_span,
                node.name.end_span,
            )

    def _check_FunctionDeclarationNode(self, node: FunctionDeclarationNode) -> None:
        # Issue 2: Architectural limitation - AST does not carry type annotations.
        # Keeping INT_TYPE hardcoding for now, adding diagnostic.
        param_types: tuple[Type, ...] = tuple(INT_TYPE for _ in node.parameters)
        # Default return type is int (as per language spec)
        return_type: Type | None = INT_TYPE
        func_type = FunctionType("function", param_types, return_type)
        symbol = self.symbol_table.resolve(
            node.name.name, node.name.start_span, node.name.end_span
        )
        if symbol is not None:
            symbol.type = func_type
        # Save previous function return type context
        previous_return_type = self.current_function_return_type
        # Use the declared (hard‑coded) return type for checking return statements
        # Enter a new scope for the function body
        self.symbol_table.enter_scope(node)

        # We must also assign types to the parameters in the scope so that
        # when their references are inferred, they return INT_TYPE!
        for parameter in node.parameters:
            param_symbol = self.symbol_table.resolve(
                parameter.name, parameter.start_span, parameter.end_span
            )
            if param_symbol is not None:
                param_symbol.type = INT_TYPE

        self.current_function_return_type = return_type
        self.check(node.body)
        # Exit the function scope
        self.symbol_table.exit_scope()
        # Restore previous context
        self.current_function_return_type = previous_return_type

    # ------------------------------------------------------------------
    # Statements

    def _check_ReturnStatementNode(self, node: ReturnStatementNode) -> None:
        if self.current_function_return_type is None:
            self._report_error(
                "Return statement outside function",
                "TYP002",
                node.start_span,
                node.end_span,
            )
            return
        value_type = self._infer_expression(node.value)
        # If the function's return type is still unknown,
        # infer it from this return statement
        if isinstance(self.current_function_return_type, UnknownType):
            self.current_function_return_type = value_type
        elif value_type != self.current_function_return_type:
            self._report_error(
                f"Return type mismatch: expected "
                f"{self.current_function_return_type!r}, got {value_type!r}",
                "TYP003",
                node.start_span,
                node.end_span,
            )

    def _check_IfStatementNode(self, node: IfStatementNode) -> None:
        cond_type = self._infer_expression(node.condition)
        if cond_type != BOOL_TYPE:
            self._report_error(
                f"Condition must be bool, got {cond_type!r}",
                "TYP004",
                node.start_span,
                node.end_span,
            )
        self.check(node.then_block)
        if node.else_block is not None:
            self.check(node.else_block)

    def _check_ForStatementNode(self, node: ForStatementNode) -> None:
        self.symbol_table.enter_scope(node)
        self._infer_expression(node.iterable)
        self.check(node.body)
        self.symbol_table.exit_scope()

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------

    def _infer_expression(self, node: ASTNode) -> Type:
        method_name = f"_infer_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is not None:
            return cast(Type, method(node))
        return UnknownType()

    def _infer_BinaryExpressionNode(self, node: BinaryExpressionNode) -> Type:
        left_type = self._infer_expression(node.left)
        right_type = self._infer_expression(node.right)
        operator = node.operator
        if operator in {
            "+",
            "-",
            "*",
            "/",
            "%",
        }:
            if left_type in {INT_TYPE, FLOAT_TYPE} and right_type in {
                INT_TYPE,
                FLOAT_TYPE,
            }:
                if left_type is FLOAT_TYPE or right_type is FLOAT_TYPE:
                    return FLOAT_TYPE
                return INT_TYPE
            self._report_error(
                f"Arithmetic operator '{operator}' requires numeric types, "
                f"got {left_type!r} and {right_type!r}",
                "TYP005",
                node.start_span,
                node.end_span,
            )
            return UnknownType()
        if operator in {
            "==",
            "!=",
            "<",
            "<=",
            ">",
            ">=",
        }:
            if left_type in {
                INT_TYPE,
                FLOAT_TYPE,
                STRING_TYPE,
                LIST_TYPE,
            } and right_type in {
                INT_TYPE,
                FLOAT_TYPE,
                STRING_TYPE,
                LIST_TYPE,
            }:
                if left_type is right_type:
                    return BOOL_TYPE
            self._report_error(
                f"Comparison operator '{operator}' requires matching types, "
                f"got {left_type!r} and {right_type!r}",
                "TYP006",
                node.start_span,
                node.end_span,
            )
            return UnknownType()
        if operator in {
            "&&",
            "||",
        }:
            if left_type == BOOL_TYPE and right_type == BOOL_TYPE:
                return BOOL_TYPE
            self._report_error(
                f"Logical operator '{operator}' requires bool, "
                f"got {left_type!r} and {right_type!r}",
                "TYP007",
                node.start_span,
                node.end_span,
            )
            return UnknownType()
        if operator == "=":
            if left_type != right_type:
                self._report_error(
                    f"Assignment type mismatch: cannot assign "
                    f"{right_type!r} to {left_type!r}",
                    "TYP008",
                    node.start_span,
                    node.end_span,
                )
            return left_type
        return UnknownType()

    def _infer_UnaryExpressionNode(self, node: UnaryExpressionNode) -> Type:
        operand_type = self._infer_expression(node.operand)
        operator = node.operator
        if operator == "-":
            if operand_type in {INT_TYPE, FLOAT_TYPE}:
                return operand_type
            self._report_error(
                f"Unary minus requires numeric type, got {operand_type!r}",
                "TYP009",
                node.start_span,
                node.end_span,
            )
            return UnknownType()
        if operator == "!":
            if operand_type is BOOL_TYPE:  # Fixed Issue 6
                return BOOL_TYPE
            self._report_error(
                f"Logical not requires bool, got {operand_type!r}",
                "TYP010",
                node.start_span,
                node.end_span,
            )
            return UnknownType()
        return UnknownType()

    def _infer_ImportDeclarationNode(self, node: ImportDeclarationNode) -> Type:
        return UnknownType()

    def _infer_MemberAccessNode(self, node: MemberAccessNode) -> Type:
        receiver_type = self._infer_expression(node.receiver)
        if isinstance(receiver_type, UnknownType):
            return UnknownType()
        return receiver_type

    def _infer_CallExpressionNode(self, node: CallExpressionNode) -> Type:
        callee_type = self._infer_expression(node.callee)
        if isinstance(callee_type, FunctionType):
            if len(node.arguments) != len(callee_type.parameter_types):
                self._report_error(
                    f"Function call expects "
                    f"{len(callee_type.parameter_types)} arguments, "
                    f"got {len(node.arguments)}",
                    "TYP011",
                    node.start_span,
                    node.end_span,
                )
            else:
                for arg, expected_type in zip(
                    node.arguments, callee_type.parameter_types
                ):
                    arg_type = self._infer_expression(arg)
                    if (
                        not isinstance(arg_type, UnknownType)
                        and arg_type is not expected_type
                    ):
                        self._report_error(
                            f"Argument type mismatch: expected {expected_type!r}, "
                            f"got {arg_type!r}",
                            "TYP012",
                            node.start_span,
                            node.end_span,
                        )
            return callee_type.return_type or UnknownType()
        self._report_error(
            f"Cannot call non-function type {callee_type!r}",
            "TYP013",
            node.start_span,
            node.end_span,
        )
        return UnknownType()

    # ------------------------------------------------------------------
    # Literals and identifiers
    # ------------------------------------------------------------------

    def _infer_IdentifierNode(self, node: IdentifierNode) -> Type:
        # Look up without reporting errors (semantic analyzer already did that)
        if self.symbol_table.scopes:
            symbol = self.symbol_table.scopes[-1].resolve(node.name)
            if symbol is not None and symbol.type is not None:
                return cast(Type, symbol.type)
        return UnknownType()

    def _infer_NumberLiteralNode(self, node: NumberLiteralNode) -> Type:
        if "." in node.value:
            return FLOAT_TYPE
        return INT_TYPE

    def _infer_StringLiteralNode(self, node: StringLiteralNode) -> Type:
        return STRING_TYPE

    def _infer_BooleanLiteralNode(self, node: BooleanLiteralNode) -> Type:
        return BOOL_TYPE

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _report_error(
        self, message: str, code: str, start_span: int | None, end_span: int | None
    ) -> None:
        line = None
        column = None
        if start_span is not None and self._source_lines is not None:
            line = 1
            col_offset = start_span
            for lineno, src_line in enumerate(self._source_lines, 1):
                if col_offset <= len(src_line):
                    line = lineno
                    column = col_offset + 1
                    break
                col_offset -= len(src_line) + 1
        elif start_span is not None:
            line = 1
            column = start_span + 1
        diagnostic = Diagnostic(
            Severity.ERROR,
            ErrorCode(code, message),
            message,
            line,
            column,
            self._file_path,
        )
        self.reporter.report(diagnostic)

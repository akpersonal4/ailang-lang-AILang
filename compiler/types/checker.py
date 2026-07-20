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
    LIST_TYPE,
    NUMERIC_UNKNOWN_TYPE,
    STRING_TYPE,
    FunctionType,
    NumericUnknownType,
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

    def _check_ProgramNode(self, node: ProgramNode) -> None:
        self.symbol_table.enter_scope(node)
        for child in node.children:
            self.check(child)
        self.symbol_table.exit_scope()

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
        expr_type = self._infer_expression(node.initializer)
        symbol = self.symbol_table.scopes[-1].resolve(node.name.name)
        if symbol is not None:
            symbol.type = expr_type
        else:
            self.symbol_table.declare(
                node.name.name,
                node.name.start_span,
                node.name.end_span,
                type=expr_type,
            )
        if isinstance(expr_type, UnknownType) and not isinstance(
            node.initializer, CallExpressionNode
        ):
            message = self._build_typ001_message(node.name.name, node.initializer)
            self._report_error(
                message,
                "TYP001",
                node.name.start_span,
                node.name.end_span,
            )

    def _check_FunctionDeclarationNode(self, node: FunctionDeclarationNode) -> None:
        param_types: tuple[Type, ...] = tuple(UnknownType() for _ in node.parameters)
        return_type: Type | None = UnknownType()
        func_type = FunctionType("function", param_types, return_type)
        symbol = self.symbol_table.scopes[-1].resolve(node.name.name)
        if symbol is not None:
            symbol.type = func_type
        else:
            self.symbol_table.declare(
                node.name.name,
                node.name.start_span,
                node.name.end_span,
                type=func_type,
            )
        previous_return_type = self.current_function_return_type
        self.symbol_table.enter_scope(node)

        for parameter in node.parameters:
            param_symbol = self.symbol_table.scopes[-1].resolve(parameter.name)
            if param_symbol is not None:
                param_symbol.type = UnknownType()
            else:
                self.symbol_table.declare(
                    parameter.name,
                    parameter.start_span,
                    parameter.end_span,
                    type=UnknownType(),
                )

        self.current_function_return_type = return_type
        self.check(node.body)
        # Write back the inferred return type (FunctionType is frozen)
        inferred_return = self.current_function_return_type
        func_type = FunctionType("function", param_types, inferred_return)
        if symbol is not None:
            symbol.type = func_type
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
        elif (
            value_type != self.current_function_return_type
            and not isinstance(value_type, (UnknownType, NumericUnknownType))
            and not isinstance(self.current_function_return_type, UnknownType)
        ):
            self._report_error(
                f"Return type mismatch: expected "
                f"{self.current_function_return_type!r}, got {value_type!r}",
                "TYP003",
                node.start_span,
                node.end_span,
            )

    def _check_IfStatementNode(self, node: IfStatementNode) -> None:
        cond_type = self._infer_expression(node.condition)
        if cond_type != BOOL_TYPE and not isinstance(cond_type, UnknownType):
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
            # String concatenation validation
            # string + string -> STRING_TYPE (valid)
            # string + UnknownType -> STRING_TYPE (valid, for inference patterns like "Hello, " + map.get(m, "key"))
            # string + NumericUnknownType/int/float/bool -> error (TYP005)
            if operator == "+" and (
                left_type is STRING_TYPE or right_type is STRING_TYPE
            ):
                # Both operands must be STRING or UnknownType (not NumericUnknownType) for valid string concatenation
                if left_type is STRING_TYPE and right_type is STRING_TYPE:
                    return STRING_TYPE
                # string + UnknownType is allowed for patterns like "prefix" + map.get(m, "key")
                # BUT NOT NumericUnknownType (that's a numeric context)
                # Use isinstance() because UnknownType is a dataclass instance, not a singleton
                left_is_unknown = isinstance(left_type, UnknownType) and not isinstance(left_type, NumericUnknownType)
                right_is_unknown = isinstance(right_type, UnknownType) and not isinstance(right_type, NumericUnknownType)
                if (left_type is STRING_TYPE and right_is_unknown) or \
                   (right_type is STRING_TYPE and left_is_unknown):
                    return STRING_TYPE
                # All other cases (string + int, float, bool, NumericUnknownType) are errors
                self._report_error(
                    f"Operator '+' requires both operands to be string when string is involved, "
                    f"got {left_type!r} and {right_type!r}",
                    "TYP005",
                    node.start_span,
                    node.end_span,
                )
                return NUMERIC_UNKNOWN_TYPE
            # Allow UnknownType/NumericUnknownType + known numeric to infer
            # to the known numeric type.
            # This enables natural patterns like map.get(m, "qty") + 1
            def _num_unk(t: Type) -> bool:
                return isinstance(t, (UnknownType, NumericUnknownType))
            if left_type is INT_TYPE and _num_unk(right_type):
                return INT_TYPE
            if right_type is INT_TYPE and _num_unk(left_type):
                return INT_TYPE
            if left_type is FLOAT_TYPE and _num_unk(right_type):
                return FLOAT_TYPE
            if right_type is FLOAT_TYPE and _num_unk(left_type):
                return FLOAT_TYPE
            if left_type in {INT_TYPE, FLOAT_TYPE} and right_type in {
                INT_TYPE,
                FLOAT_TYPE,
            }:
                if left_type is FLOAT_TYPE or right_type is FLOAT_TYPE:
                    return FLOAT_TYPE
                return INT_TYPE
            # M76.2A: Unknown + Unknown → NumericUnknownType.
            # Both operands are unknown but used in arithmetic context.
            if _num_unk(left_type) and _num_unk(right_type):
                return NUMERIC_UNKNOWN_TYPE
            if not _num_unk(left_type) and not _num_unk(right_type):
                self._report_error(
                    f"Arithmetic operator '{operator}' requires numeric types, "
                    f"got {left_type!r} and {right_type!r}",
                    "TYP005",
                    node.start_span,
                    node.end_span,
                )
            return NUMERIC_UNKNOWN_TYPE
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
                BOOL_TYPE,
            } and right_type in {
                INT_TYPE,
                FLOAT_TYPE,
                STRING_TYPE,
                LIST_TYPE,
                BOOL_TYPE,
            }:
                if left_type is right_type:
                    return BOOL_TYPE
            # Comparisons always return bool even with unknown operands
            def _num_unk(t: Type) -> bool:
                return isinstance(t, (UnknownType, NumericUnknownType))
            if _num_unk(left_type) or _num_unk(right_type):
                return BOOL_TYPE
            if not _num_unk(left_type) and not _num_unk(right_type):
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
            if not isinstance(left_type, UnknownType) and not isinstance(
                right_type, UnknownType
            ):
                self._report_error(
                    f"Logical operator '{operator}' requires bool, "
                    f"got {left_type!r} and {right_type!r}",
                    "TYP007",
                    node.start_span,
                    node.end_span,
                )
            return UnknownType()
        if operator == "=":
            if (
                left_type != right_type
                and not isinstance(left_type, UnknownType)
                and not isinstance(right_type, (UnknownType, NumericUnknownType))
                and right_type is not INT_TYPE
            ):
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
            if not isinstance(operand_type, (UnknownType, NumericUnknownType)):
                self._report_error(
                    f"Unary minus requires numeric type, got {operand_type!r}",
                    "TYP009",
                    node.start_span,
                    node.end_span,
                )
            return operand_type
        if operator == "!":
            if operand_type is BOOL_TYPE:  # Fixed Issue 6
                return BOOL_TYPE
            if not isinstance(operand_type, UnknownType):
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
        if isinstance(receiver_type, (UnknownType, NumericUnknownType)):
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
                        not isinstance(expected_type, UnknownType)
                        and not isinstance(arg_type, UnknownType)
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
        if not isinstance(callee_type, UnknownType):
            self._report_error(
                f"Cannot call non-function type {callee_type!r}",
                "TYP013",
                node.start_span,
                node.end_span,
            )
        elif isinstance(node.callee, IdentifierNode):
            sym = self.symbol_table.scopes[-1].resolve(node.callee.name)
            if sym is None:
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

    def _format_expression(self, node: ASTNode) -> str:
        """Format an AST node as a human-readable expression string."""
        if isinstance(node, BinaryExpressionNode):
            left = self._format_expression(node.left)
            right = self._format_expression(node.right)
            return f"{left} {node.operator} {right}"
        if isinstance(node, UnaryExpressionNode):
            operand = self._format_expression(node.operand)
            return f"{node.operator}{operand}"
        if isinstance(node, CallExpressionNode):
            callee = self._format_expression(node.callee)
            args = ", ".join(self._format_expression(a) for a in node.arguments)
            return f"{callee}({args})"
        if isinstance(node, MemberAccessNode):
            receiver = self._format_expression(node.receiver)
            return f"{receiver}.{node.member.name}"
        if isinstance(node, IdentifierNode):
            return node.name
        if isinstance(node, NumberLiteralNode):
            return node.value
        if isinstance(node, StringLiteralNode):
            return f'"{node.value}"'
        if isinstance(node, BooleanLiteralNode):
            return "true" if node.value else "false"
        return "..."

    def _build_typ001_message(self, var_name: str, expr_node: ASTNode) -> str:
        """Build a rich TYP001 diagnostic message with expression and operand info."""
        expr_str = self._format_expression(expr_node)
        lines = [f"Cannot infer type for variable '{var_name}'"]
        lines.append("")
        lines.append("Expression:")
        lines.append(f"    {expr_str}")

        # For binary expressions, show operand types
        if isinstance(expr_node, BinaryExpressionNode):
            left_type = self._infer_expression(expr_node.left)
            right_type = self._infer_expression(expr_node.right)
            left_str = self._format_expression(expr_node.left)
            right_str = self._format_expression(expr_node.right)
            lines.append("")
            lines.append("Operand types:")
            lines.append(f"    {left_str} -> {left_type!r}")
            lines.append(f"    {right_str} -> {right_type!r}")

        lines.append("")
        lines.append("Suggestions:")
        lines.append("    - Use explicit conversion helpers (convert.to_int, convert.to_string).")
        lines.append("    - Initialize values using typed literals (let x = 0; let s = \"\").")
        lines.append("    - Check return types of upstream functions with ail explain.")
        return "\n".join(lines)

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

"""Runtime interpreter for AILang IR."""

from __future__ import annotations

from typing import Any

from compiler.ir.nodes import (
    AssignmentIR,
    BinaryOperationIR,
    BlockIR,
    CallIR,
    ExpressionStatementIR,
    FunctionIR,
    IfIR,
    IRNode,
    LiteralIR,
    ProgramIR,
    ReturnIR,
    UnaryOperationIR,
    VariableDeclarationIR,
    VariableReferenceIR,
)

from .builtins import BUILTINS
from .environment import Environment
from .stack_frame import StackFrame


class ReturnSignal:
    """Used to propagate return values out of a function body."""

    def __init__(self, value: Any) -> None:
        self.value = value


class Runtime:
    """Execute a lowered IR program with lexical scopes and frames."""

    def __init__(self) -> None:
        self._global_environment = Environment()
        self._frame_stack: list[StackFrame] = []
        self._functions: dict[str, FunctionIR] = {}

    def execute(self, program: ProgramIR) -> Any:
        result: Any = None
        for node in program.body:
            result = self._execute_node(node)
        if "main" in self._functions:
            return self._call_function(self._functions["main"], ())
        return result

    def _execute_node(self, node: IRNode) -> Any:
        if isinstance(node, ProgramIR):
            return self.execute(node)
        if isinstance(node, FunctionIR):
            self._functions[node.name] = node
            self._global_environment.define(node.name, node)
            return None
        if isinstance(node, VariableDeclarationIR):
            value = self._evaluate_expression(node.initializer)
            self._set_local(node.name, value)
            return value
        if isinstance(node, AssignmentIR):
            value = self._evaluate_expression(node.value)
            self._set_local(node.target, value)
            return value
        if isinstance(node, IfIR):
            condition = self._evaluate_expression(node.condition)
            if condition:
                return self._execute_block(node.then_block)
            if node.else_block is not None:
                return self._execute_block(node.else_block)
            return None
        if isinstance(node, ReturnIR):
            return ReturnSignal(self._evaluate_expression(node.value))
        if isinstance(node, ExpressionStatementIR):
            if isinstance(node.expression, AssignmentIR):
                return self._execute_node(node.expression)
            return self._evaluate_expression(node.expression)
        if isinstance(node, BlockIR):
            return self._execute_block(node)
        if isinstance(node, BinaryOperationIR):
            return self._evaluate_expression(node)
        if isinstance(node, UnaryOperationIR):
            return self._evaluate_expression(node)
        if isinstance(node, CallIR):
            return self._evaluate_expression(node)
        if isinstance(node, LiteralIR):
            return node.value
        if isinstance(node, VariableReferenceIR):
            return self._get_local(node.name)
        raise TypeError(f"Unsupported IR node: {type(node)!r}")

    def _execute_block(self, block: BlockIR) -> Any:
        result: Any = None
        for statement in block.statements:
            result = self._execute_node(statement)
            if isinstance(statement, ReturnIR) or isinstance(result, ReturnSignal):
                return result
        return result

    def _call_function(self, function: FunctionIR, args: tuple[Any, ...]) -> Any:
        if len(args) != len(function.parameters):
            raise TypeError(
                f"Function {function.name} expected {len(function.parameters)} "
                f"arguments, got {len(args)}"
            )
        frame = StackFrame(
            function_name=function.name,
            parent_frame=self._frame_stack[-1] if self._frame_stack else None,
        )
        for name, value in zip(function.parameters, args, strict=True):
            frame.define(name, value)
        self._frame_stack.append(frame)
        try:
            result = self._execute_block(function.body)
            if isinstance(result, ReturnSignal):
                return result.value
            return result
        finally:
            self._frame_stack.pop()

    def _evaluate_expression(self, expression: Any) -> Any:
        if isinstance(expression, BinaryOperationIR):
            left = self._evaluate_expression(expression.left)
            right = self._evaluate_expression(expression.right)
            if expression.operator == "+":
                return left + right
            if expression.operator == "-":
                return left - right
            if expression.operator == "*":
                return left * right
            if expression.operator == "/":
                return left / right
            if expression.operator == "%":
                return left % right
            if expression.operator == "==":
                return left == right
            if expression.operator == "!=":
                return left != right
            if expression.operator == "<":
                return left < right
            if expression.operator == "<=":
                return left <= right
            if expression.operator == ">":
                return left > right
            if expression.operator == ">=":
                return left >= right
            if expression.operator == "&&":
                return bool(left and right)
            if expression.operator == "||":
                return bool(left or right)
            raise ValueError(f"Unsupported operator: {expression.operator}")
        if isinstance(expression, UnaryOperationIR):
            operand = self._evaluate_expression(expression.operand)
            if expression.operator == "-":
                return -operand
            if expression.operator == "!":
                return not operand
            raise ValueError(f"Unsupported operator: {expression.operator}")
        if isinstance(expression, CallIR):
            callee = self._get_local(expression.callee)
            if isinstance(callee, FunctionIR):
                args = tuple(
                    self._evaluate_expression(arg) for arg in expression.arguments
                )
                return self._call_function(callee, args)
            if expression.callee in BUILTINS:
                args = tuple(
                    self._evaluate_expression(arg) for arg in expression.arguments
                )
                return BUILTINS[expression.callee](args)
            raise TypeError(f"Cannot call non-function: {expression.callee}")
        if isinstance(expression, LiteralIR):
            return expression.value
        if isinstance(expression, VariableReferenceIR):
            return self._get_local(expression.name)
        raise TypeError(f"Unsupported expression: {type(expression)!r}")

    def _set_local(self, name: str, value: Any) -> None:
        if self._frame_stack:
            self._frame_stack[-1].assign(name, value)
        else:
            self._global_environment.define(name, value)

    def _get_local(self, name: str) -> Any:
        if self._frame_stack:
            try:
                return self._frame_stack[-1].resolve(name)
            except NameError:
                pass
        try:
            return self._global_environment.resolve(name)
        except NameError:
            pass
        if name in BUILTINS:
            return BUILTINS[name]
        raise NameError(f"Undefined variable: {name}")

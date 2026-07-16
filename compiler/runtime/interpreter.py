"""Runtime interpreter for AILang IR."""

from __future__ import annotations

import sys
from typing import Any, Dict

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
    MemberAccessIR,
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

    def __init__(self, module_bundle: Any = None) -> None:
        sys.setrecursionlimit(50000)
        self._global_environment = Environment()
        self._frame_stack: list[StackFrame] = []
        self._functions: dict[str, FunctionIR] = {}
        self._modules: dict[str, Any] = {}  # module_name -> module environment
        self._aliases: dict[str, str] = {}  # alias -> real_module_name
        self._module_bundle = module_bundle
        self._initialized_modules: set[str] = set()

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
            self._define_local(node.name, value)
            return value
        if isinstance(node, AssignmentIR):
            value = self._evaluate_expression(node.value)
            self._assign_local(node.target, value)
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
        frame = StackFrame(
            parent_frame=self._frame_stack[-1] if self._frame_stack else None,
        )
        self._frame_stack.append(frame)
        try:
            result: Any = None
            for statement in block.statements:
                result = self._execute_node(statement)
                if isinstance(statement, ReturnIR) or isinstance(result, ReturnSignal):
                    return result
            return result
        finally:
            self._frame_stack.pop()

    def _call_function(self, function: FunctionIR, args: tuple[Any, ...]) -> Any:
        total = len(function.parameters)
        defaults = {
            name: self._evaluate_expression(expr)
            for name, expr in function.default_parameters
        }
        required = total - len(defaults)
        if len(args) < required or len(args) > total:
            raise TypeError(
                f"Function {function.name} expected {required}-{total} "
                f"arguments, got {len(args)}"
            )
        frame = StackFrame(
            function_name=function.name,
            parent_frame=self._frame_stack[-1] if self._frame_stack else None,
        )
        for name, value in zip(function.parameters, args):
            frame.define(name, value)
        for name in function.parameters[len(args):]:
            if name in defaults:
                frame.define(name, defaults[name])
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
        if isinstance(expression, MemberAccessIR):
            receiver = self._evaluate_expression(expression.receiver)
            member = expression.member
            # Handle module function access: math.add -> look up module + function
            if isinstance(receiver, Environment):
                func = receiver.resolve(member)
                if func is not None:
                    return func
            # Handle dict-style access
            if isinstance(receiver, dict):
                return receiver.get(member)
            if hasattr(receiver, member):
                return getattr(receiver, member)
            return receiver
        if isinstance(expression, UnaryOperationIR):
            operand = self._evaluate_expression(expression.operand)
            if expression.operator == "-":
                return -operand
            if expression.operator == "!":
                return not operand
            raise ValueError(f"Unsupported operator: {expression.operator}")
        if isinstance(expression, CallIR):
            # callee can be a string (function name) or an expression
            if isinstance(expression.callee, str):
                callee = self._resolve_name(expression.callee)
            else:
                callee = self._evaluate_expression(expression.callee)

            # Handle callable (built-in or regular function)
            if isinstance(callee, FunctionIR):
                args = tuple(
                    self._evaluate_expression(arg) for arg in expression.arguments
                )
                return self._call_function(callee, args)

            # callable() handles both functions and built-ins
            if callable(callee):
                args = tuple(
                    self._evaluate_expression(arg) for arg in expression.arguments
                )
                if isinstance(callee, FunctionIR):
                    return self._call_function(callee, args)
                if callee in BUILTINS.values():
                    return callee(args)
                try:
                    return callee(*args)
                except TypeError:
                    return callee(args)

            raise TypeError(f"Cannot call non-function: {callee}")

        if isinstance(expression, LiteralIR):
            return expression.value
        if isinstance(expression, VariableReferenceIR):
            return self._get_local(expression.name)
        raise TypeError(f"Unsupported expression: {type(expression)!r}")

    def _define_local(self, name: str, value: Any) -> None:
        if self._frame_stack:
            self._frame_stack[-1].define(name, value)
        else:
            self._global_environment.define(name, value)

    def _assign_local(self, name: str, value: Any) -> None:
        if self._frame_stack:
            self._frame_stack[-1].assign(name, value)
        else:
            self._global_environment.define(name, value)

    def _initialize_module(self, module_name: str) -> Environment | None:
        """Initialize a module exactly once, following dependency order.

        Returns:
            The module environment if initialization succeeded, None otherwise.
        """
        if module_name in self._initialized_modules:
            return self._modules.get(module_name)

        if self._module_bundle is None:
            return None

        module_ir = self._module_bundle.module_irs.get(module_name)
        if module_ir is None:
            return None

        # Create module environment
        module_env = Environment()

        # Execute module-level code
        for node in module_ir.body:
            self._execute_node_in_module(module_name, module_env, node)

        self._modules[module_name] = module_env
        self._initialized_modules.add(module_name)

        # Register import aliases for this module in both the alias dict
        # and the global environment so they're accessible during execution
        if self._module_bundle is not None:
            aliases = getattr(self._module_bundle, 'import_aliases', {}).get(module_name, {})
            for alias, real_module in aliases.items():
                self._aliases[alias] = real_module
                # Also define the alias as a module reference in global env
                module_env = self._modules.get(real_module)
                if module_env is not None:
                    self._global_environment.define(alias, module_env)

        return module_env

    def _execute_node_in_module(
        self, module_name: str, module_env: Environment, node: IRNode
    ) -> Any:
        """Execute an IR node in the context of a module's environment."""
        if isinstance(node, FunctionIR):
            # Register function with both unqualified and qualified names so
            # that ``math.add(...)`` resolves via ``_get_local("math.add")``.
            qualified_name = f"{module_name}.{node.name}"
            self._functions[qualified_name] = node
            self._functions[node.name] = node
            self._global_environment.define(node.name, node)
            self._global_environment.define(qualified_name, node)
            module_env.define(node.name, node)
            return None
        # Default execution
        return self._execute_node(node)

    def _resolve_name(self, name: str) -> Any:
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
        module_env = self._modules.get(name)
        if module_env is not None:
            return module_env
        # Check import aliases
        if name in self._aliases:
            real_module = self._aliases[name]
            module_env = self._modules.get(real_module)
            if module_env is not None:
                return module_env
        if "." in name:
            base_name, member = name.split(".", 1)
            try:
                receiver = self._get_local(base_name)
            except NameError:
                receiver = None
            if receiver is not None:
                if isinstance(receiver, Environment):
                    try:
                        return receiver.resolve(member)
                    except NameError:
                        pass
                if isinstance(receiver, dict):
                    return receiver.get(member)
                if hasattr(receiver, member):
                    return getattr(receiver, member)

            module_env = self._modules.get(base_name)
            if module_env is not None:
                try:
                    return module_env.resolve(member)
                except NameError:
                    pass
        raise NameError(f"Undefined variable: {name}")

    def _get_local(self, name: str) -> Any:
        return self._resolve_name(name)

    def get_cache_info(self) -> list[dict[str, Any]]:
        """Return cache info for all active environments (testing hook)."""
        infos: list[dict[str, Any]] = []
        infos.append({"scope": "global", **self._global_environment.get_cache_info()})
        for frame in self._frame_stack:
            name = frame.function_name or "anonymous"
            infos.append(
                {"scope": f"frame:{name}", **frame.environment.get_cache_info()}
            )
        return infos

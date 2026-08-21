"""Runtime interpreter for AILang IR."""

from __future__ import annotations

import sys
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
    MemberAccessIR,
    ProgramIR,
    ReturnIR,
    UnaryOperationIR,
    VariableDeclarationIR,
    VariableReferenceIR,
)

from .builtins import BUILTINS
from .environment import Environment
from .errors import RuntimeError
from .stack_frame import StackFrame


class ReturnSignal:
    """Used to propagate return values out of a function body."""

    def __init__(self, value: Any) -> None:
        self.value = value


# Sentinel returned by _evaluate_expression when a CallIR is trampolined
# (pushed to _trampoline_stack) instead of executed immediately.  The
# caller (binary-op handler, etc.) uses this to detect the deferral and
# set up _trampoline_pending_binary.
_TRAMPOLINE_SENTINEL = object()


class _TrampolinePendingBinary:
    """Stores a binary operation waiting for a trampolined call to complete.

    When the left operand of a binary expression is a trampolined function call,
    the operation cannot be completed immediately.  This object records the
    operator and the **pre-evaluated** right operand so the trampoline loop can
    finish the operation without needing the caller's scope.
    """

    __slots__ = ("operator", "right_value")

    def __init__(self, operator: str, right_value: Any) -> None:
        self.operator = operator
        self.right_value = right_value


class _TailCallSentinel:
    """Sentinel returned by _execute_block to signal a tail-call for inline chaining.

    When a tail-call is detected at depth > 1 and the call arguments contain
    no recursive CallIRs (e.g. ``build_records(n - 1, items)``), _execute_block
    returns this sentinel instead of recursing through the Python host stack.
    ``_inline_tail_chain`` drains the chain iteratively.
    """

    __slots__ = ("function", "args")

    def __init__(self, function: FunctionIR, args: tuple[Any, ...]) -> None:
        self.function = function
        self.args = args


class Runtime:
    """Execute a lowered IR program with lexical scopes and frames."""

    def __init__(self, module_bundle: Any = None) -> None:
        from .sandbox import get_policy

        policy = get_policy()
        # Set Python recursionlimit safely above our own limit so CPython
        # never catches a RecursionError before our AILang-level depth check.
        # Each AILang function call consumes several Python stack frames
        # (call machinery + environment resolve chains), so the Python limit
        # must be a multiple of the AILang limit.
        self._max_call_depth = policy.max_recursion
        self._call_depth = 0
        sys.setrecursionlimit(max(self._max_call_depth * 10 + 1000, 15000))
        self._global_environment = Environment()
        self._frame_stack: list[StackFrame] = []
        self._functions: dict[str, FunctionIR] = {}
        self._modules: dict[str, Any] = {}  # module_name -> module environment
        self._aliases: dict[str, str] = {}  # alias -> real_module_name
        self._module_bundle = module_bundle
        self._initialized_modules: set[str] = set()
        # Maps id(FunctionIR) -> owning module name. FunctionIR is a frozen
        # dataclass, so we cannot attach a runtime-only attribute to it; the
        # id-keyed mapping is set in _execute_node_in_module and read in
        # _call_function to decide whether the callee is a stdlib wrapper.
        self._function_modules: dict[int, str] = {}
        # Module source map for runtime error location: module_name -> (file_path, source_text)
        self._source_map: dict[str, tuple[str, str]] = {}
        # Current expression source span being evaluated
        self._current_span: int | None = None
        # Monotonic set of names that have been bound in some frame during
        # this run. Used to skip the frame-chain walk in `_resolve_name` when
        # the name is guaranteed not to be visible via dynamic scoping,
        # turning per-row module-name resolution from O(call_depth) into O(1).
        # Safe by construction: names are only added, never removed, and a
        # name that *was* frame-bound but is no longer present (its frame
        # has popped) merely causes a wasted walk, never an incorrect result.
        self._frame_ever_bound: set[str] = set()
        # --- Trampoline (ADR-017) ---
        # Explicit call stack for iterative execution of tail-recursive calls.
        # Replaces Python host-stack recursion for tail-call positions,
        # removing the ~2000-frame ceiling imposed by CPython's stack limit.
        # Each entry is (function, args, parent_frame) where parent_frame is
        # the StackFrame that was active when the tail call was detected,
        # needed to preserve the lexical scope chain across trampoline iterations.
        self._trampoline_stack: list[tuple[FunctionIR, tuple[Any, ...], StackFrame | None]] = []
        # Stack of pending binary operations: when the left side of a binary
        # expression is a trampolined call, the operation is deferred and
        # pushed here.  The trampoline loop completes each once the deferred
        # call returns.  A stack (not a single value) is needed because
        # nested patterns like ``f(x) + g(y) + 1`` produce multiple pending
        # operations at different nesting levels.
        self._trampoline_pending_binaries: list[_TrampolinePendingBinary] = []
        # Flag set by _execute_block before evaluating a tail-call return
        # expression.  When True, _evaluate_expression will trampoline
        # FunctionIR calls instead of recursing through the Python host stack.
        self._trampoline_tail_call_active: bool = False
        # Total number of trampoline iterations in the current top-level call.
        # Used to enforce the recursion depth limit even though the Python
        # host stack is no longer growing.
        self._trampoline_iterations: int = 0
        # Depth of nested function calls initiated by the trampoline loop.
        # Incremented/decremented in _call_function.  At depth==1, tail
        # calls are pushed to the trampoline stack.  At depth>1 with safe
        # arguments (no CallIR): tail calls use _inline_tail_chain for
        # iterative draining without nested trampolines.  At depth>1 with
        # recursive arguments (e.g. ack(m-1, ack(m, n-1))): fall through
        # to normal Python recursion to avoid infinite trampoline nesting.
        self._trampoline_depth: int = 0

    def execute(self, program: ProgramIR) -> Any:
        try:
            result: Any = None
            for node in program.body:
                result = self._execute_node(node)
            if "main" in self._functions:
                return self._trampoline_call(self._functions["main"], ())
            return result
        except RuntimeError:
            raise
        except RecursionError as exc:
            raise self._augment_error(RuntimeError(
                operation="call",
                reason=(
                    "Recursion depth exceeded. AILang recursion is bounded "
                    "to prevent stack overflow."
                ),
                suggestion=(
                    "Simplify recursive logic or increase the recursion "
                    "limit via the sandbox policy."
                ),
            )) from exc
        except FileNotFoundError as exc:
            raise self._augment_error(RuntimeError(
                operation="file.read",
                reason=f"File not found: {getattr(exc, 'filename', 'unknown path')}",
                suggestion="Check that the file exists and the path is correct.",
            )) from exc
        except PermissionError as exc:
            raise self._augment_error(RuntimeError(
                operation="sandbox",
                reason=str(exc),
                suggestion=(
                    "The AILang sandbox restricts file access to the project "
                    "directory. Use --no-sandbox to disable it."
                ),
            )) from exc
        except UnicodeDecodeError as exc:
            raise self._augment_error(RuntimeError(
                operation="file.read",
                reason="File is not valid UTF-8.",
                suggestion="Re-save the file as UTF-8.",
            )) from exc
        except Exception as exc:
            raise self._augment_error(RuntimeError(
                operation="runtime",
                reason=f"Unexpected error: {type(exc).__name__}: {exc}",
                suggestion="This is an internal error. Please report it.",
            )) from exc

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
                # --- Trampoline tail-call detection (ADR-017) ---
                # Detect tail-call patterns in the IR BEFORE evaluating
                # the expression, so we can push to the trampoline stack
                # instead of recursing through the Python host stack.
                if isinstance(statement, ReturnIR):
                    rv_node = statement.value
                    # Pattern 1: return f(args)  — direct tail call
                    # Three strategies based on depth and argument safety:
                    #   depth==1:  push to trampoline stack, return None
                    #   depth>1, args safe (no CallIR): inline tail chain
                    #   depth>1, args unsafe (has CallIR): fall through to
                    #            normal execution (avoids infinite nesting
                    #            for ackermann-style nested recursion)
                    if self._is_tail_call(rv_node):
                        callee = self._functions[rv_node.callee]
                        has_call_args = any(
                            isinstance(a, CallIR) for a in rv_node.arguments
                        )
                        if self._trampoline_depth == 1:
                            call_args = tuple(
                                self._evaluate_expression(a)
                                for a in rv_node.arguments
                            )
                            parent = (
                                self._frame_stack[-1]
                                if self._frame_stack
                                else None
                            )
                            self._trampoline_stack.append(
                                (callee, call_args, parent)
                            )
                            return None  # trampoline loop will process next frame
                        elif not has_call_args:
                            call_args = tuple(
                                self._evaluate_expression(a)
                                for a in rv_node.arguments
                            )
                            return _TailCallSentinel(callee, call_args)
                        # else: fall through to normal execution below
                    # Pattern 2: return f(args) + simple_expr — tail call
                    # with binary op.  Only activate when the right operand
                    # is a simple expression (literal or variable) that can
                    # be safely pre-evaluated in the current scope.  Complex
                    # right operands (e.g. fib(n-2)) would themselves trigger
                    # recursion and must not be deferred.
                    if (
                        isinstance(rv_node, BinaryOperationIR)
                        and self._is_tail_call(rv_node.left)
                        and isinstance(
                            rv_node.right,
                            (LiteralIR, VariableReferenceIR),
                        )
                    ):
                        # Pre-evaluate the right operand NOW while the
                        # function frame is still on the stack.
                        right_val = self._evaluate_expression(rv_node.right)
                        if self._trampoline_depth == 1:
                            self._trampoline_tail_call_active = True
                            left_val = self._evaluate_expression(rv_node.left)
                            self._trampoline_tail_call_active = False
                            if left_val is _TRAMPOLINE_SENTINEL:
                                self._trampoline_pending_binaries.append(
                                    _TrampolinePendingBinary(
                                        rv_node.operator, right_val
                                    )
                                )
                                return None
                            return ReturnSignal(
                                self._apply_binary(
                                    rv_node.operator, left_val, right_val
                                )
                            )
                        else:
                            has_call_args = any(
                                isinstance(a, CallIR)
                                for a in rv_node.left.arguments
                            )
                            if not has_call_args:
                                call_args = tuple(
                                    self._evaluate_expression(a)
                                    for a in rv_node.left.arguments
                                )
                                callee = self._functions[rv_node.left.callee]
                                left_val = self._inline_tail_chain(
                                    callee, call_args
                                )
                                return ReturnSignal(
                                    self._apply_binary(
                                        rv_node.operator, left_val, right_val
                                    )
                                )
                result = self._execute_node(statement)
                if isinstance(result, _TailCallSentinel):
                    return result
                if isinstance(statement, ReturnIR) or isinstance(result, ReturnSignal):
                    return result
            return result
        finally:
            self._frame_stack.pop()

    def _call_function(self, function: FunctionIR, args: tuple[Any, ...]) -> Any:
        # Snapshot the user-side call-site span before executing the callee.
        # When the callee is a stdlib wrapper that itself calls a native
        # builtin, the native's span belongs to a stdlib source file and is
        # useless for the user; _augment_error uses call_span instead.
        caller_span = self._current_span
        self._call_depth += 1
        self._trampoline_depth += 1
        if self._call_depth > self._max_call_depth:
            self._call_depth -= 1
            self._trampoline_depth -= 1
            raise self._augment_error(RuntimeError(
                operation="call",
                reason=(
                    f"Recursion depth exceeded (limit: {self._max_call_depth}). "
                    "AILang recursion is bounded to prevent stack overflow."
                ),
                suggestion=(
                    "Simplify recursive logic. The recursion limit is fixed at "
                    f"{self._max_call_depth} in this build; for larger iterations "
                    "use multiple smaller batches."
                ),
            ))
        total = len(function.parameters)
        defaults = {
            name: self._evaluate_expression(expr)
            for name, expr in function.default_parameters
        }
        required = total - len(defaults)
        if len(args) < required or len(args) > total:
            self._call_depth -= 1
            self._trampoline_depth -= 1
            raise self._augment_error(RuntimeError(
                operation="function_call",
                reason=(
                    f"Function `{function.name}` expects {required}-{total} "
                    f"argument(s), got {len(args)}."
                ),
                suggestion="Check the function signature and provide the correct number of arguments.",
            ))
        frame = StackFrame(
            function_name=function.name,
            parent_frame=self._frame_stack[-1] if self._frame_stack else None,
        )
        frame.call_span = caller_span
        frame.module = self._function_modules.get(id(function))
        for name, value in zip(function.parameters, args):
            frame.define(name, value)
            self._frame_ever_bound.add(name)
        for name in function.parameters[len(args) :]:
            if name in defaults:
                frame.define(name, defaults[name])
                self._frame_ever_bound.add(name)
        self._frame_stack.append(frame)
        try:
            result = self._execute_block(function.body)
            if isinstance(result, ReturnSignal):
                return result.value
            if isinstance(result, _TailCallSentinel):
                return self._inline_tail_chain(result.function, result.args)
            return result
        finally:
            self._frame_stack.pop()
            self._call_depth -= 1
            self._trampoline_depth -= 1

    # ------------------------------------------------------------------
    # Trampoline (ADR-017 Option E)
    # ------------------------------------------------------------------

    def _is_tail_call(self, expression: Any) -> bool:
        """Return True if *expression* is a CallIR targeting a FunctionIR
        (not a builtin).  Used to detect tail-call positions where the
        interpreter can defer the call to the trampoline stack instead of
        recursing through the Python host stack."""
        if not isinstance(expression, CallIR):
            return False
        if isinstance(expression.callee, str):
            callee = self._functions.get(expression.callee)
            return callee is not None
        return False

    def _trampoline_call(self, function: FunctionIR, args: tuple[Any, ...]) -> Any:
        """Entry point for trampolined execution.

        Pushes the initial call frame onto the trampoline stack and drives
        the iterative execution loop.  Tail-recursive calls detected during
        ``_execute_block`` are pushed to the stack instead of recursing,
        keeping the Python host-stack depth at O(1) regardless of AILang
        recursion depth.

        Each trampoline entry carries a saved parent frame so that the
        lexical scope chain is preserved across trampoline iterations.

        This method is re-entrant: when called from a function that is itself
        being executed by an outer trampoline (depth > 1), it saves and
        restores all trampoline state so nested tail-call chains run in an
        isolated trampoline without corrupting the outer one.
        """
        # Save any existing trampoline state for re-entrant calls (depth > 1).
        saved_stack = self._trampoline_stack
        saved_pending = self._trampoline_pending_binaries
        saved_iterations = self._trampoline_iterations
        saved_tail_active = self._trampoline_tail_call_active
        saved_depth = self._trampoline_depth

        # Initialize fresh trampoline state for this call.
        self._trampoline_stack = [(function, args, None)]
        self._trampoline_pending_binaries = []
        self._trampoline_iterations = 0
        self._trampoline_tail_call_active = False
        self._trampoline_depth = 0

        try:
            result: Any = None

            while self._trampoline_stack:
                fn, fn_args, parent_frame = self._trampoline_stack.pop()

                # Enforce the recursion depth limit across trampoline iterations.
                # The trampoline bypasses the Python host stack, so it can handle
                # much deeper recursion than _max_call_depth.  Use a 50x multiplier
                # to allow the canonical 10k workload while still catching runaway
                # iterations.
                self._trampoline_iterations += 1
                if self._trampoline_iterations > self._max_call_depth * 50:
                    raise self._augment_error(RuntimeError(
                        operation="call",
                        reason=(
                            f"Recursion depth exceeded "
                            f"(limit: {self._max_call_depth * 50}). "
                            "AILang recursion is bounded to prevent stack overflow."
                        ),
                        suggestion=(
                            "Simplify recursive logic. The recursion limit is "
                            f"{self._max_call_depth * 50} iterations per "
                            "trampoline loop; for larger iterations use multiple "
                            "smaller batches."
                        ),
                    ))

                # Temporarily restore the parent frame so _call_function creates
                # a frame with the correct lexical parent, preserving the scope
                # chain for variables declared in calling functions.
                saved_frame_stack = self._frame_stack
                if parent_frame is not None:
                    self._frame_stack = [parent_frame]
                else:
                    self._frame_stack = []
                try:
                    result = self._call_function(fn, fn_args)
                finally:
                    self._frame_stack = saved_frame_stack

                # Complete any pending binary operations when the stack is empty
                # (base case reached).  The right operand was pre-evaluated when
                # the pending binary was created, so no scope is needed.
                if not self._trampoline_stack:
                    while self._trampoline_pending_binaries:
                        pending = self._trampoline_pending_binaries.pop()
                        result = self._apply_binary(
                            pending.operator, result, pending.right_value
                        )

            return result
        finally:
            # Restore outer trampoline state (no-op for top-level calls).
            self._trampoline_stack = saved_stack
            self._trampoline_pending_binaries = saved_pending
            self._trampoline_iterations = saved_iterations
            self._trampoline_tail_call_active = saved_tail_active
            self._trampoline_depth = saved_depth

    def _inline_tail_chain(self, function: FunctionIR, args: tuple[Any, ...]) -> Any:
        """Drain a tail-call chain iteratively without growing the host stack.

        Called at depth > 1 when the tail-call arguments contain no recursive
        CallIRs (e.g. ``build_records(n - 1, items)``).  Sets up frames
        directly instead of going through ``_call_function`` to avoid inflating
        ``_call_depth`` / ``_trampoline_depth`` and triggering nested trampoline
        creation for argument evaluations.

        When the function body detects another tail call (Pattern 1), it
        returns a ``_TailCallSentinel`` which this method uses to loop with
        the new callee and arguments.

        Per-call-chain iteration budget (ADR-018 Option C): each chain gets
        an independent iteration budget of ``_max_call_depth * 50``.  The
        counter is saved on entry and restored on exit (including exception
        paths) so that independent chains do not share a cumulative budget.
        """
        # ADR-018 §8.1: save and reset iteration counter for this chain.
        saved_iterations = self._trampoline_iterations
        self._trampoline_iterations = 0
        try:
            while True:
                # ADR-018 lines 534–535: increment and enforce per-chain budget.
                self._trampoline_iterations += 1
                if self._trampoline_iterations > self._max_call_depth * 50:
                    raise self._augment_error(RuntimeError(
                        operation="call",
                        reason=(
                            f"Recursion depth exceeded "
                            f"(limit: {self._max_call_depth * 50}). "
                            "AILang recursion is bounded to prevent stack overflow."
                        ),
                        suggestion=(
                            "Simplify recursive logic. The recursion limit is "
                            f"{self._max_call_depth * 50} iterations per call "
                            "chain; for larger iterations use multiple smaller "
                            "batches."
                        ),
                    ))

                # Set up frame directly (like _call_function without depth tracking).
                frame = StackFrame(
                    function_name=function.name,
                    parent_frame=self._frame_stack[-1] if self._frame_stack else None,
                )
                for name, value in zip(function.parameters, args):
                    frame.define(name, value)
                    self._frame_ever_bound.add(name)

                self._frame_stack.append(frame)
                try:
                    result = self._execute_block(function.body)
                finally:
                    self._frame_stack.pop()

                if isinstance(result, ReturnSignal):
                    result = result.value

                if isinstance(result, _TailCallSentinel):
                    function = result.function
                    args = result.args
                    continue

                return result
        finally:
            # ADR-018 §8.3: restore previous counter so enclosing scope
            # is unaffected by this chain's iterations.
            self._trampoline_iterations = saved_iterations

    def _apply_binary(self, op: str, left: Any, right: Any) -> Any:
        """Evaluate a binary operation on pre-evaluated operands."""
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            try:
                return left / right
            except ZeroDivisionError:
                raise self._augment_error(RuntimeError(
                    operation="division",
                    reason="Division by zero is undefined.",
                    expected_type="non-zero divisor",
                    actual_type="0",
                    suggestion="Guard division with a check for zero.",
                ))
        if op == "%":
            try:
                return left % right
            except ZeroDivisionError:
                raise self._augment_error(RuntimeError(
                    operation="modulo",
                    reason="Modulo by zero is undefined.",
                    expected_type="non-zero divisor",
                    actual_type="0",
                    suggestion="Guard modulo with a check for zero.",
                ))
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right
        if op == "&&":
            return bool(left and right)
        if op == "||":
            return bool(left or right)
        raise ValueError(f"Unsupported operator: {op}")

    def _evaluate_expression(self, expression: Any) -> Any:
        # Track the source span of the expression being evaluated so a
        # runtime error can be reported at the offending line. Previously
        # only CallIR updated _current_span, which left division-by-zero
        # and member-access errors with no line number at all.
        span = getattr(expression, "start_span", None)
        if span is not None:
            self._current_span = span
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
                try:
                    return left / right
                except ZeroDivisionError:
                    raise self._augment_error(RuntimeError(
                        operation="division",
                        reason="Division by zero is undefined.",
                        expected_type="non-zero divisor",
                        actual_type="0",
                        suggestion="Guard division with a check for zero.",
                    ))
            if expression.operator == "%":
                try:
                    return left % right
                except ZeroDivisionError:
                    raise self._augment_error(RuntimeError(
                        operation="modulo",
                        reason="Modulo by zero is undefined.",
                        expected_type="non-zero divisor",
                        actual_type="0",
                        suggestion="Guard modulo with a check for zero.",
                    ))
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
                    if member.startswith("__") and member.endswith("__"):
                        _ALLOWED_DUNDER = frozenset({
                            "__len__", "__str__", "__repr__", "__bool__", "__contains__",
                            "__iter__", "__next__",
                            "__getitem__", "__setitem__", "__delitem__",
                            "__add__", "__sub__", "__mul__", "__truediv__",
                            "__floordiv__", "__mod__", "__pow__",
                            "__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__",
                            "__hash__", "__int__", "__float__", "__index__",
                            "__neg__", "__pos__", "__abs__", "__invert__",
                            "__and__", "__or__", "__xor__", "__lshift__", "__rshift__",
                        })
                        if member not in _ALLOWED_DUNDER:
                            raise self._augment_error(RuntimeError(
                                operation="attribute_access",
                                reason=f"Access to dunder attribute '{member}' is not allowed.",
                                suggestion="Only safe data-model methods are accessible. Use public APIs only.",
                            ))
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
            # Track current source span for error diagnostics
            self._current_span = expression.start_span

            # callee can be a string (function name) or an expression
            if isinstance(expression.callee, str):
                callee = self._resolve_name(expression.callee)
            else:
                callee = self._evaluate_expression(expression.callee)

            # Handle callable (built-in or regular function)
            if isinstance(callee, FunctionIR):
                # --- Trampoline: detect tail-call position (ADR-017) ---
                # When this CallIR is the immediate return value of the
                # enclosing function and targets a user FunctionIR (not a
                # builtin), push the call to the trampoline stack instead
                # of recursing through the Python host stack.  This keeps
                # the Python host-stack depth at O(1).
                if self._trampoline_tail_call_active and self._is_tail_call(expression) and self._trampoline_depth == 1:
                    args = tuple(
                        self._evaluate_expression(arg) for arg in expression.arguments
                    )
                    # Save the parent frame to preserve the scope chain.
                    parent = (
                        self._frame_stack[-1]
                        if self._frame_stack
                        else None
                    )
                    self._trampoline_stack.append((callee, args, parent))
                    self._trampoline_tail_call_active = False
                    return _TRAMPOLINE_SENTINEL
                args = tuple(
                    self._evaluate_expression(arg) for arg in expression.arguments
                )
                # Restore the span of THIS call before entering the callee so
                # the callee's wrapper sees the user's call-site span.
                self._current_span = expression.start_span
                return self._call_function(callee, args)

            # callable() handles both functions and built-ins
            if callable(callee):
                args = tuple(
                    self._evaluate_expression(arg) for arg in expression.arguments
                )
                # Restore the user-side span before invoking the callable
                # (for BUILTIN dispatch the callee path on line ~311 is
                # taken before this branch).
                self._current_span = expression.start_span
                if isinstance(callee, FunctionIR):
                    return self._call_function(callee, args)
                if callee in BUILTINS.values():
                    try:
                        return callee(args)
                    except RuntimeError as re:
                        raise self._augment_error(re)
                try:
                    return callee(*args)
                except TypeError:
                    return callee(args)

            raise self._augment_error(RuntimeError(
                operation="call",
                reason=f"Cannot call non-function value.",
                expected_type="function or callable",
                actual_type=RuntimeError._type_name(callee),
                suggestion="Ensure the name refers to a function, not a variable.",
            ))

        if isinstance(expression, LiteralIR):
            return expression.value
        if isinstance(expression, VariableReferenceIR):
            return self._get_local(expression.name)
        raise TypeError(f"Unsupported expression: {type(expression)!r}")

    def set_source_map(self, source_map: dict[str, tuple[str, str]]) -> None:
        """Set the source map for runtime error location resolution.

        Args:
            source_map: Mapping of module_name -> (file_path, source_text).
        """
        self._source_map = source_map

    def call_function(self, name: str, args: tuple[Any, ...] = ()) -> Any:
        """Call a user-defined function by name after module initialization.

        This is the public entry point used by tooling (e.g. ``ail test``)
        to invoke ``test_*`` functions that would otherwise only run when
        referenced from ``main()``.

        Args:
            name: Unqualified function name (e.g. ``test_addition``).
            args: Positional arguments, if any.

        Returns:
            The function's return value.

        Raises:
            RuntimeError: If the function is not defined.
        """
        function = self._functions.get(name)
        if function is None:
            raise self._augment_error(RuntimeError(
                operation="call",
                reason=f"Unknown function '{name}'.",
                suggestion=(
                    "Check that the function is defined in a module that "
                    "was discovered by the compiler."
                ),
            ))
        return self._trampoline_call(function, tuple(args))

    def _augment_error(self, error: RuntimeError) -> RuntimeError:
        """Inject source location into a RuntimeError if not already set.

        The challenge: AILang's stdlib is a thin AILang wrapper around a
        Python builtin. When the wrapper invokes the builtin, _current_span
        is rewritten to a span inside the stdlib source file, which would
        otherwise be mapped against the user's source and produce a bogus
        line. The fix: if the innermost executing function is a stdlib
        wrapper, report the user's call-site span (``frame.call_span``)
        against the user's source file.
        """
        if error.source_file:
            return error
        # Find the innermost function frame (block frames have no name).
        fn_frame: StackFrame | None = None
        for frame in reversed(self._frame_stack):
            if frame.function_name:
                fn_frame = frame
                break
        if (
            fn_frame is not None
            and fn_frame.module is not None
            and self._is_stdlib_module(fn_frame.module)
        ):
            for file_path, source_text in self._source_map.values():
                if "stdlib" not in str(file_path):
                    error.source_file = file_path
                    span = (
                        fn_frame.call_span
                        if fn_frame.call_span is not None
                        else self._current_span
                    )
                    if span is not None:
                        error.source_line = RuntimeError._span_to_line(
                            source_text, span
                        )
                    return error
        # Fallback: use the current expression span against the first user
        # module so errors are not misattributed to a stdlib source file.
        if self._source_map and not error.source_file:
            user_entry: tuple[str, str] | None = None
            for file_path, source_text in self._source_map.values():
                if "stdlib" not in str(file_path):
                    user_entry = (file_path, source_text)
                    break
            if user_entry is None:
                user_entry = next(iter(self._source_map.values()))
            error.source_file = user_entry[0]
            if self._current_span is not None:
                error.source_line = RuntimeError._span_to_line(
                    user_entry[1], self._current_span
                )
        return error

    def _is_stdlib_module(self, module_name: str | None) -> bool:
        """Return True if ``module_name`` is backed by a file under stdlib/."""
        if module_name is None:
            return False
        entry = self._source_map.get(module_name)
        if entry is None:
            return False
        return "stdlib" in str(entry[0])

    def _define_local(self, name: str, value: Any) -> None:
        if self._frame_stack:
            self._frame_stack[-1].define(name, value)
            self._frame_ever_bound.add(name)
        else:
            self._global_environment.define(name, value)

    def _assign_local(self, name: str, value: Any) -> None:
        if self._frame_stack:
            self._frame_stack[-1].assign(name, value)
            # An assign may introduce a new binding in the frame chain
            # (e.g. when no ancestor has the name). Track it so future
            # resolves of `name` still consult the frame chain instead of
            # skipping straight to the global / module lookup.
            self._frame_ever_bound.add(name)
        else:
            self._global_environment.define(name, value)

    def _initialize_module(
        self, module_name: str, run_body: bool = True
    ) -> Environment | None:
        """Initialize a module exactly once, following dependency order.

        Args:
            module_name: Name of the module to initialize.
            run_body: When False, skip executing module-level body statements
                (function/let registrations) and only register the module
                environment plus import aliases. Used by ``cmd_run`` for the
                user's entry module so that ``runtime.execute(program_ir)``
                runs the entry body exactly once.

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

        # Execute module-level code (skipped for the user entry module,
        # whose body is executed by ``runtime.execute`` to guarantee a
        # single execution).
        if run_body:
            for node in module_ir.body:
                self._execute_node_in_module(module_name, module_env, node)

        self._modules[module_name] = module_env
        self._initialized_modules.add(module_name)

        # Register import aliases for this module in both the alias dict
        # and the global environment so they're accessible during execution
        if self._module_bundle is not None:
            aliases = getattr(self._module_bundle, "import_aliases", {}).get(
                module_name, {}
            )
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
            # Record the owning module so _call_function can later decide
            # whether the callee is a stdlib wrapper (call site belongs to
            # the user's source file) or user code.
            self._function_modules[id(node)] = module_name
            return None
        # Default execution
        return self._execute_node(node)

    def _resolve_name(self, name: str) -> Any:
        if self._frame_stack:
            # Stdlib wrappers call internal binding names (list_copy, dict_new,
            # ...) directly. Resolve those to the builtin BEFORE consulting
            # user scopes so a user-declared helper with the same name cannot
            # hijack a stdlib implementation. The top frame is a block frame
            # (module=None); the innermost *function* frame owns the module.
            if name in BUILTINS:
                fn_frame: StackFrame | None = None
                for frame in reversed(self._frame_stack):
                    if frame.function_name:
                        fn_frame = frame
                        break
                if fn_frame is not None and self._is_stdlib_module(fn_frame.module):
                    return BUILTINS[name]
            # Fast path: if `name` has never been bound in any frame on the
            # current stack (and all prior frames this run), the chain walk
            # is guaranteed to raise NameError. Skip it and fall through to
            # the global / builtin / module lookup. This turns the
            # per-row module-name resolution that dominates large recursive
            # programs (e.g. ledger-style row helpers calling `convert.to_string`)
            # from O(call_depth) into O(1). Dynamic scoping is preserved:
            # names that *are* (or have been) frame-bound still walk the chain.
            if name in self._frame_ever_bound:
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
                    # Deny-by-default for dunder attributes — only explicitly
                    # allowed data-model methods are accessible.
                    if member.startswith("__") and member.endswith("__"):
                        _ALLOWED_DUNDER = frozenset({
                            "__len__", "__str__", "__repr__", "__bool__", "__contains__",
                            "__iter__", "__next__",
                            "__getitem__", "__setitem__", "__delitem__",
                            "__add__", "__sub__", "__mul__", "__truediv__",
                            "__floordiv__", "__mod__", "__pow__",
                            "__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__",
                            "__hash__", "__int__", "__float__", "__index__",
                            "__neg__", "__pos__", "__abs__", "__invert__",
                            "__and__", "__or__", "__xor__", "__lshift__", "__rshift__",
                        })
                        if member not in _ALLOWED_DUNDER:
                            raise self._augment_error(RuntimeError(
                                operation="attribute_access",
                                reason=f"Access to dunder attribute '{member}' is not allowed.",
                                suggestion="Only safe data-model methods are accessible. Use public APIs only.",
                            ))
                    return getattr(receiver, member)

            module_env = self._modules.get(base_name)
            if module_env is not None:
                try:
                    return module_env.resolve(member)
                except NameError:
                    pass
        raise self._augment_error(RuntimeError(
            operation="variable_lookup",
            reason=f"Undefined variable `{name}`.",
            suggestion="Check that the variable is defined and the name is spelled correctly.",
        ))

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

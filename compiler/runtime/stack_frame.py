"""Execution frames for the runtime."""

from __future__ import annotations

from typing import Any

from .environment import Environment


class StackFrame:
    """A runtime execution frame with local values and a parent frame."""

    def __init__(
        self,
        function_name: str | None = None,
        parent_frame: StackFrame | None = None,
        environment: Environment | None = None,
    ) -> None:
        self.function_name = function_name
        self.parent_frame = parent_frame
        self.environment: Environment = environment or Environment(
            parent=parent_frame.environment if parent_frame is not None else None
        )
        self.return_value: Any = None

    def define(self, name: str, value: Any) -> None:
        self.environment.define(name, value)

    def assign(self, name: str, value: Any) -> None:
        self.environment.assign(name, value)

    def resolve(self, name: str) -> Any:
        return self.environment.resolve(name)

    def set_return_value(self, value: Any) -> None:
        self.return_value = value

    @property
    def locals(self) -> dict[str, Any]:
        return self.environment.values

"""Lexical runtime environments for AILang."""

from __future__ import annotations

from typing import Any


class Environment:
    """A lexical runtime scope with parent lookup semantics."""

    def __init__(self, parent: Environment | None = None) -> None:
        self._values: dict[str, Any] = {}
        self._parent = parent

    def define(self, name: str, value: Any) -> None:
        self._values[name] = value

    def assign(self, name: str, value: Any) -> None:
        if name in self._values:
            self._values[name] = value
            return
        if self._parent is not None:
            self._parent.assign(name, value)
            return
        self.define(name, value)

    def resolve(self, name: str) -> Any:
        if name in self._values:
            return self._values[name]
        if self._parent is not None:
            return self._parent.resolve(name)
        raise NameError(f"Undefined variable: {name}")

    @property
    def values(self) -> dict[str, Any]:
        return self._values

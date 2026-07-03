"""Shared runtime value typing helpers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeAlias

RuntimeValue: TypeAlias = Any
BuiltinCallable: TypeAlias = Callable[[tuple[RuntimeValue, ...]], RuntimeValue]

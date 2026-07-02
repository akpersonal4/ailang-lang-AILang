"""Type system definitions for AILang."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@runtime_checkable
class Type(Protocol):
    @property
    def name(self) -> str: ...


@dataclass(frozen=True)
class PrimitiveType:
    name: str

    def __repr__(self) -> str:
        return self.name


@dataclass(frozen=True)
class FunctionType:
    name: str = "function"
    parameter_types: tuple[Type, ...] = ()
    return_type: Type | None = None

    def __repr__(self) -> str:
        return (
            f"fn({', '.join(repr(t) for t in self.parameter_types)}) -> "
            f"{self.return_type!r}"
        )


@dataclass(frozen=True)
class UnknownType:
    name: str = "unknown"

    def __repr__(self) -> str:
        return self.name


# Primitive types
INT_TYPE: Type = PrimitiveType("int")
STRING_TYPE: Type = PrimitiveType("string")
BOOL_TYPE: Type = PrimitiveType("bool")
FLOAT_TYPE: Type = PrimitiveType("float")

PRIMITIVE_TYPES = {
    "int": INT_TYPE,
    "string": STRING_TYPE,
    "bool": BOOL_TYPE,
    "float": FLOAT_TYPE,
}

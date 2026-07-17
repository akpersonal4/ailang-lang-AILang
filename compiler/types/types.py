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


@dataclass(frozen=True)
class NumericUnknownType:
    """Unknown type that participates in arithmetic operations.

    This type represents values whose type cannot be determined at compile time,
    but which are known to be used in numeric contexts. It allows arithmetic
    expressions like `map.get() + map.get()` to type-check without requiring
    explicit initialization workarounds.

    Unlike UnknownType, NumericUnknownType:
    - Participates in arithmetic inference (Unknown + NumericUnknown → NumericUnknown)
    - Does NOT participate in string concatenation (would error)
    - Still validates at runtime by Python
    """

    name: str = "numeric_unknown"

    def __repr__(self) -> str:
        return self.name


# Primitive types
INT_TYPE: Type = PrimitiveType("int")
STRING_TYPE: Type = PrimitiveType("string")
BOOL_TYPE: Type = PrimitiveType("bool")
FLOAT_TYPE: Type = PrimitiveType("float")
LIST_TYPE: Type = PrimitiveType("list")

# Numeric unknown type for M76.2
NUMERIC_UNKNOWN_TYPE: Type = NumericUnknownType()

PRIMITIVE_TYPES = {
    "int": INT_TYPE,
    "string": STRING_TYPE,
    "bool": BOOL_TYPE,
    "float": FLOAT_TYPE,
    "list": LIST_TYPE,
}

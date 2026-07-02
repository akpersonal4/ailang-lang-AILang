"""Type system package for AILang."""

from compiler.types.checker import TypeChecker
from compiler.types.types import (
    FunctionType,
    PrimitiveType,
    Type,
    UnknownType,
)

__all__ = [
    "TypeChecker",
    "Type",
    "PrimitiveType",
    "FunctionType",
    "UnknownType",
]

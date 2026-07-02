"""Intermediate Representation (IR) package for AILang.

This package provides immutable IR node definitions, a builder that lowers the
AST into IR, a validator for structural checks, and a printer for deterministic
textual representation used in golden‑file tests.
"""

from .builder import IRBuilder as IRBuilder
from .nodes import *  # noqa: F403
from .printer import IRPrinter as IRPrinter
from .validator import (
    IRValidationError as IRValidationError,
)
from .validator import (
    IRValidator as IRValidator,
)

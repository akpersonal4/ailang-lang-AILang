"""Built-in runtime functions for AILang."""

from __future__ import annotations

from typing import Any

from .values import RuntimeValue


def print_builtin(args: tuple[RuntimeValue, ...]) -> None:
    if not args:
        print()
        return
    print(*args)


BUILTINS: dict[str, Any] = {"print": print_builtin}

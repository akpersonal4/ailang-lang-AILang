from __future__ import annotations

from dataclasses import dataclass, field

from compiler.lexer import Token


@dataclass
class CSTNode:
    kind: str
    children: list[CSTNode] = field(default_factory=list)
    token: Token | None = None
    start_span: int | None = None
    end_span: int | None = None

    def __str__(self) -> str:
        lines = [self.kind]
        for child in self.children:
            child_lines = str(child).splitlines()
            for child_line in child_lines:
                lines.append(f"  {child_line}")
        return "\n".join(lines)

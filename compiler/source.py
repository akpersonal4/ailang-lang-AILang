from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Source:
    """Represents a source file loaded into memory."""

    path: Path
    text: str

    @classmethod
    def from_file(cls, path: str | Path) -> Source:
        file_path = Path(path)
        return cls(path=file_path, text=file_path.read_text(encoding="utf-8"))

    @property
    def lines(self) -> list[str]:
        return self.text.splitlines()

    def line(self, index: int) -> str:
        if index < 1 or index > len(self.lines):
            raise IndexError("line index out of range")
        return self.lines[index - 1]

    def __len__(self) -> int:
        return len(self.text)

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class SourceEncodingError(Exception):
    """Raised when a source file cannot be decoded as UTF-8.

    AILang source files must be UTF-8 encoded. This error exists so the
    compiler can emit a clean user-facing diagnostic instead of leaking a
    raw UnicodeDecodeError traceback.
    """

    def __init__(self, path: str, detail: str) -> None:
        self.path = path
        self.detail = detail
        super().__init__(f"Source file is not valid UTF-8: {path}")


@dataclass(frozen=True)
class Source:
    """Represents a source file loaded into memory."""

    path: Path
    text: str

    @classmethod
    def from_file(cls, path: str | Path) -> Source:
        file_path = Path(path)
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            raise SourceEncodingError(
                str(file_path),
                f"file is not valid UTF-8 (byte {e.start}): {e.reason}",
            ) from e
        return cls(path=file_path, text=text)

    @property
    def lines(self) -> list[str]:
        return self.text.splitlines()

    def line(self, index: int) -> str:
        if index < 1 or index > len(self.lines):
            raise IndexError("line index out of range")
        return self.lines[index - 1]

    def __len__(self) -> int:
        return len(self.text)

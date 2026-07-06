"""LSP type definitions and JSON-RPC helpers."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any, cast

# ---------------------------------------------------------------------------
# JSON-RPC wire protocol
# ---------------------------------------------------------------------------


def _read_message() -> dict[str, Any] | None:
    """Read a single JSON-RPC message from stdin (LSP transport)."""
    content_length = 0
    headers_read = False
    for raw_line in sys.stdin.buffer:
        line = raw_line.decode("utf-8", errors="replace").strip()
        if not line and headers_read:
            break
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":")[1].strip())
            headers_read = True

    if content_length == 0:
        return None

    body = sys.stdin.buffer.read(content_length)
    body = body.decode("utf-8", errors="replace")
    if not body:
        return None
    return cast(dict[str, Any], json.loads(body))


def _send_message(obj: dict[str, Any]) -> None:
    """Send a JSON-RPC message to stdout (LSP transport)."""
    body = json.dumps(obj, ensure_ascii=False)
    data = body.encode("utf-8")
    header = f"Content-Length: {len(data)}\r\n\r\n"
    sys.stdout.buffer.write(header.encode("ascii") + data)
    sys.stdout.buffer.flush()


# ---------------------------------------------------------------------------
# LSP position / range types
# ---------------------------------------------------------------------------


@dataclass
class Position:
    line: int  # 0-based
    character: int  # 0-based

    def to_dict(self) -> dict[str, int]:
        return {"line": self.line, "character": self.character}


@dataclass
class Range:
    start: Position
    end: Position

    def to_dict(self) -> dict[str, dict[str, int]]:
        return {"start": self.start.to_dict(), "end": self.end.to_dict()}


@dataclass
class Location:
    uri: str
    range: Range

    def to_dict(self) -> dict[str, Any]:
        return {"uri": self.uri, "range": self.range.to_dict()}


# ---------------------------------------------------------------------------
# LSP diagnostic types
# ---------------------------------------------------------------------------


@dataclass
class Diagnostic:
    range: Range
    message: str
    severity: int = 1  # 1=Error, 2=Warning, 3=Info, 4=Hint
    source: str = "ailang"

    def to_dict(self) -> dict[str, Any]:
        return {
            "range": self.range.to_dict(),
            "message": self.message,
            "severity": self.severity,
            "source": self.source,
        }


# ---------------------------------------------------------------------------
# Completion types
# ---------------------------------------------------------------------------


@dataclass
class CompletionItem:
    label: str
    kind: int = 14  # 14=Function, 6=Method, 9=Module, 15=Variable, 4=Class
    detail: str = ""
    insert_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "kind": self.kind,
            "detail": self.detail,
            "insertText": self.insert_text or None,
        }


# ---------------------------------------------------------------------------
# Hover types
# ---------------------------------------------------------------------------


@dataclass
class Hover:
    contents: str
    range: Range | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "contents": {"kind": "markdown", "value": self.contents}
        }
        if self.range is not None:
            result["range"] = self.range.to_dict()
        return result


# ---------------------------------------------------------------------------
# Signature help types
# ---------------------------------------------------------------------------


@dataclass
class ParameterInformation:
    label: str
    documentation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"label": self.label, "documentation": self.documentation}


@dataclass
class SignatureInformation:
    label: str
    documentation: str = ""
    parameters: list[ParameterInformation] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "documentation": self.documentation,
            "parameters": [p.to_dict() for p in self.parameters],
        }


@dataclass
class SignatureHelp:
    signatures: list[SignatureInformation]
    active_signature: int = 0
    active_parameter: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "signatures": [s.to_dict() for s in self.signatures],
            "activeSignature": self.active_signature,
            "activeParameter": self.active_parameter,
        }


# ---------------------------------------------------------------------------
# Symbol types
# ---------------------------------------------------------------------------


@dataclass
class SymbolInformation:
    name: str
    kind: int  # LSP SymbolKind
    location: Location
    container_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "location": self.location.to_dict(),
            "containerName": self.container_name,
        }


# ---------------------------------------------------------------------------
# Utility: offset → LSP position
# ---------------------------------------------------------------------------


def offset_to_position(offset: int, text: str) -> Position:
    """Convert a byte offset in source text to a 0-based LSP Position."""
    if offset < 0:
        return Position(0, 0)
    line = 0
    col = 0
    for i, ch in enumerate(text):
        if i == offset:
            return Position(line, col)
        if ch == "\n":
            line += 1
            col = 0
        else:
            col += 1
    return Position(line, col)

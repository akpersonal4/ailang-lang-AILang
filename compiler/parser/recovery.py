from __future__ import annotations

from compiler.lexer import TokenKind
from compiler.parser.token_stream import TokenStream


def synchronize(stream: TokenStream) -> None:
    """Advance to the next safe synchronization boundary."""
    while not stream.is_at_end():
        if stream.current().kind in {TokenKind.SEMICOLON, TokenKind.RBRACE}:
            break
        stream.advance()

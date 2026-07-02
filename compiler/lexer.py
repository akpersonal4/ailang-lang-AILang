from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TokenKind(Enum):
    IDENTIFIER = "identifier"
    NUMBER = "number"
    ASSIGN = "assign"
    EOF = "eof"


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    value: str
    start: int
    end: int


class Lexer:
    def tokenize(self, text: str) -> list[Token]:
        tokens: list[Token] = []
        index = 0
        length = len(text)

        while index < length:
            char = text[index]
            if char.isspace():
                index += 1
                continue
            if char.isalpha() or char == "_":
                start = index
                index += 1
                while index < length and (text[index].isalnum() or text[index] == "_"):
                    index += 1
                tokens.append(
                    Token(TokenKind.IDENTIFIER, text[start:index], start, index)
                )
                continue
            if char.isdigit():
                start = index
                index += 1
                while index < length and text[index].isdigit():
                    index += 1
                tokens.append(Token(TokenKind.NUMBER, text[start:index], start, index))
                continue
            if char == "=":
                tokens.append(Token(TokenKind.ASSIGN, char, index, index + 1))
                index += 1
                continue
            raise ValueError(f"Unexpected character: {char}")

        tokens.append(Token(TokenKind.EOF, "", length, length))
        return tokens

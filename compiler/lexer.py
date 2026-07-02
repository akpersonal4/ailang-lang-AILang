from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TokenKind(Enum):
    IDENTIFIER = "identifier"
    NUMBER = "number"
    ASSIGN = "assign"
    LET = "let"
    FN = "fn"
    IF = "if"
    ELSE = "else"
    RETURN = "return"
    LPAREN = "lparen"
    RPAREN = "rparen"
    LBRACE = "lbrace"
    RBRACE = "rbrace"
    COMMA = "comma"
    SEMICOLON = "semicolon"
    PLUS = "plus"
    MINUS = "minus"
    STAR = "star"
    SLASH = "slash"
    PERCENT = "percent"
    EQEQ = "eqeq"
    NEQ = "neq"
    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"
    ANDAND = "andand"
    OROR = "oror"
    BANG = "bang"
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
                text_value = text[start:index]
                keyword_kind = {
                    "let": TokenKind.LET,
                    "fn": TokenKind.FN,
                    "if": TokenKind.IF,
                    "else": TokenKind.ELSE,
                    "return": TokenKind.RETURN,
                }.get(text_value)
                if keyword_kind is None:
                    tokens.append(Token(TokenKind.IDENTIFIER, text_value, start, index))
                else:
                    tokens.append(Token(keyword_kind, text_value, start, index))
                continue
            if char.isdigit():
                start = index
                index += 1
                while index < length and text[index].isdigit():
                    index += 1
                tokens.append(Token(TokenKind.NUMBER, text[start:index], start, index))
                continue
            if char == "=":
                if index + 1 < length and text[index + 1] == "=":
                    tokens.append(Token(TokenKind.EQEQ, "==", index, index + 2))
                    index += 2
                else:
                    tokens.append(Token(TokenKind.ASSIGN, char, index, index + 1))
                    index += 1
                continue
            if char == "!":
                if index + 1 < length and text[index + 1] == "=":
                    tokens.append(Token(TokenKind.NEQ, "!=", index, index + 2))
                    index += 2
                else:
                    tokens.append(Token(TokenKind.BANG, char, index, index + 1))
                    index += 1
                continue
            if char == "<":
                if index + 1 < length and text[index + 1] == "=":
                    tokens.append(Token(TokenKind.LTE, "<=", index, index + 2))
                    index += 2
                else:
                    tokens.append(Token(TokenKind.LT, char, index, index + 1))
                    index += 1
                continue
            if char == ">":
                if index + 1 < length and text[index + 1] == "=":
                    tokens.append(Token(TokenKind.GTE, ">=", index, index + 2))
                    index += 2
                else:
                    tokens.append(Token(TokenKind.GT, char, index, index + 1))
                    index += 1
                continue
            if char == "&":
                if index + 1 < length and text[index + 1] == "&":
                    tokens.append(Token(TokenKind.ANDAND, "&&", index, index + 2))
                    index += 2
                else:
                    raise ValueError(f"Unexpected character: {char}")
                continue
            if char == "|":
                if index + 1 < length and text[index + 1] == "|":
                    tokens.append(Token(TokenKind.OROR, "||", index, index + 2))
                    index += 2
                else:
                    raise ValueError(f"Unexpected character: {char}")
                continue
            if char == "+":
                tokens.append(Token(TokenKind.PLUS, char, index, index + 1))
                index += 1
                continue
            if char == "-":
                tokens.append(Token(TokenKind.MINUS, char, index, index + 1))
                index += 1
                continue
            if char == "*":
                tokens.append(Token(TokenKind.STAR, char, index, index + 1))
                index += 1
                continue
            if char == "/":
                tokens.append(Token(TokenKind.SLASH, char, index, index + 1))
                index += 1
                continue
            if char == "%":
                tokens.append(Token(TokenKind.PERCENT, char, index, index + 1))
                index += 1
                continue
            if char == "(":
                tokens.append(Token(TokenKind.LPAREN, char, index, index + 1))
                index += 1
                continue
            if char == ")":
                tokens.append(Token(TokenKind.RPAREN, char, index, index + 1))
                index += 1
                continue
            if char == "{":
                tokens.append(Token(TokenKind.LBRACE, char, index, index + 1))
                index += 1
                continue
            if char == "}":
                tokens.append(Token(TokenKind.RBRACE, char, index, index + 1))
                index += 1
                continue
            if char == ",":
                tokens.append(Token(TokenKind.COMMA, char, index, index + 1))
                index += 1
                continue
            if char == ";":
                tokens.append(Token(TokenKind.SEMICOLON, char, index, index + 1))
                index += 1
                continue
            raise ValueError(f"Unexpected character: {char}")

        tokens.append(Token(TokenKind.EOF, "", length, length))
        return tokens

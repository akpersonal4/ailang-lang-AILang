from __future__ import annotations

from compiler.lexer import TokenKind
from compiler.parser.nodes import CSTNode
from compiler.parser.token_stream import TokenStream


def parse_expression(stream: TokenStream) -> CSTNode:
    return parse_assignment_expression(stream)


def parse_assignment_expression(stream: TokenStream) -> CSTNode:
    left = parse_logical_or_expression(stream)
    if stream.match(TokenKind.ASSIGN):
        right = parse_assignment_expression(stream)
        return CSTNode("AssignmentExpression", [left, right])
    return left


def parse_logical_or_expression(stream: TokenStream) -> CSTNode:
    left = parse_logical_and_expression(stream)
    while stream.current().kind is TokenKind.OROR:
        operator = stream.advance()
        right = parse_logical_and_expression(stream)
        left = CSTNode(
            "BinaryExpression",
            [left, right],
            operator,
            start_span=left.start_span,
            end_span=right.end_span,
        )
    return left


def parse_logical_and_expression(stream: TokenStream) -> CSTNode:
    left = parse_equality_expression(stream)
    while stream.current().kind is TokenKind.ANDAND:
        operator = stream.advance()
        right = parse_equality_expression(stream)
        left = CSTNode(
            "BinaryExpression",
            [left, right],
            operator,
            start_span=left.start_span,
            end_span=right.end_span,
        )
    return left


def parse_equality_expression(stream: TokenStream) -> CSTNode:
    left = parse_comparison_expression(stream)
    while stream.current().kind in {TokenKind.EQEQ, TokenKind.NEQ}:
        operator = stream.advance()
        right = parse_comparison_expression(stream)
        left = CSTNode(
            "BinaryExpression",
            [left, right],
            operator,
            start_span=left.start_span,
            end_span=right.end_span,
        )
    return left


def parse_comparison_expression(stream: TokenStream) -> CSTNode:
    left = parse_additive_expression(stream)
    while stream.current().kind in {
        TokenKind.LT,
        TokenKind.LTE,
        TokenKind.GT,
        TokenKind.GTE,
    }:
        operator = stream.advance()
        right = parse_additive_expression(stream)
        left = CSTNode(
            "BinaryExpression",
            [left, right],
            operator,
            start_span=left.start_span,
            end_span=right.end_span,
        )
    return left


def parse_additive_expression(stream: TokenStream) -> CSTNode:
    left = parse_multiplicative_expression(stream)
    while stream.current().kind in {TokenKind.PLUS, TokenKind.MINUS}:
        operator = stream.advance()
        right = parse_multiplicative_expression(stream)
        left = CSTNode(
            "BinaryExpression",
            [left, right],
            operator,
            start_span=left.start_span,
            end_span=right.end_span,
        )
    return left


def parse_multiplicative_expression(stream: TokenStream) -> CSTNode:
    left = parse_unary_expression(stream)
    while stream.current().kind in {
        TokenKind.STAR,
        TokenKind.SLASH,
        TokenKind.PERCENT,
    }:
        operator = stream.advance()
        right = parse_unary_expression(stream)
        left = CSTNode(
            "BinaryExpression",
            [left, right],
            operator,
            start_span=left.start_span,
            end_span=right.end_span,
        )
    return left


def parse_unary_expression(stream: TokenStream) -> CSTNode:
    if stream.current().kind in {TokenKind.MINUS, TokenKind.BANG}:
        operator = stream.advance()
        operand = parse_unary_expression(stream)
        return CSTNode(
            "UnaryExpression",
            [operand],
            operator,
            start_span=operator.start_offset,
            end_span=operand.end_span,
        )
    return parse_postfix_expression(stream)


def parse_postfix_expression(stream: TokenStream) -> CSTNode:
    expression = parse_primary_expression(stream)
    while True:
        if stream.match(TokenKind.LPAREN):
            argument_list = parse_argument_list(stream)
            stream.expect(TokenKind.RPAREN)
            expression = CSTNode(
                "CallExpression",
                [expression, argument_list],
                start_span=expression.start_span,
                end_span=argument_list.end_span,
            )
        elif stream.match(TokenKind.DOT):
            member = parse_identifier(stream)
            expression = CSTNode(
                "MemberAccess",
                [expression, member],
                start_span=expression.start_span,
                end_span=member.end_span,
            )
        else:
            break
    return expression


def parse_argument_list(stream: TokenStream) -> CSTNode:
    arguments = CSTNode("ArgumentList")
    arguments.start_span = stream.current().start_offset
    if stream.current().kind is not TokenKind.RPAREN:
        arguments.children.append(parse_expression(stream))
        while stream.match(TokenKind.COMMA):
            arguments.children.append(parse_expression(stream))
    arguments.end_span = stream.previous().end_offset
    return arguments


def parse_primary_expression(stream: TokenStream) -> CSTNode:
    if stream.current().kind is TokenKind.NUMBER:
        token = stream.advance()
        return CSTNode(
            "NumberLiteral",
            token=token,
            start_span=token.start_offset,
            end_span=token.end_offset,
        )
    if stream.current().kind is TokenKind.STRING:
        token = stream.advance()
        return CSTNode(
            "StringLiteral",
            token=token,
            start_span=token.start_offset,
            end_span=token.end_offset,
        )
    if stream.current().kind in {TokenKind.TRUE, TokenKind.FALSE}:
        token = stream.advance()
        return CSTNode(
            "BooleanLiteral",
            token=token,
            start_span=token.start_offset,
            end_span=token.end_offset,
        )
    if stream.current().kind is TokenKind.IDENTIFIER:
        return parse_identifier(stream)
    if stream.match(TokenKind.LPAREN):
        expression = parse_expression(stream)
        stream.expect(TokenKind.RPAREN)
        return expression
    stream.report("Expected expression")
    return CSTNode("MissingExpression")


def parse_identifier(stream: TokenStream) -> CSTNode:
    token = stream.current()
    if stream.match(TokenKind.IDENTIFIER):
        return CSTNode(
            "Identifier",
            token=token,
            start_span=token.start_offset,
            end_span=token.end_offset,
        )
    stream.report("Expected identifier")
    return CSTNode("Identifier")

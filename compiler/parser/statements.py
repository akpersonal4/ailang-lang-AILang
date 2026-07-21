"""Statement-level parser functions for AILang."""

from __future__ import annotations

from compiler.lexer import TokenKind
from compiler.parser.declarations import (
    parse_function_declaration,
    parse_variable_declaration,
)
from compiler.parser.expressions import parse_expression
from compiler.parser.nodes import CSTNode
from compiler.parser.recovery import synchronize
from compiler.parser.token_stream import TokenStream


def parse_block(stream: TokenStream) -> CSTNode:
    block = CSTNode("Block")
    block.start_span = stream.current().start_offset
    stream.expect(TokenKind.LBRACE)
    max_iterations = 10000  # safety guard against infinite loops
    iterations = 0
    while not stream.is_at_end() and stream.current().kind is not TokenKind.RBRACE:
        iterations += 1
        if iterations > max_iterations:
            stream.report(
                "Too many statements in block (infinite loop detected)", "PAR002"
            )
            break
        if stream.current().kind is TokenKind.LET:
            block.children.append(parse_variable_declaration(stream))
        elif stream.current().kind is TokenKind.RETURN:
            block.children.append(parse_return_statement(stream))
        elif stream.current().kind is TokenKind.FN:
            block.children.append(parse_function_declaration(stream))
        elif stream.current().kind is TokenKind.IF:
            block.children.append(parse_if_statement(stream))
        elif stream.current().kind is TokenKind.SEMICOLON:
            # Skip empty statements
            stream.advance()
        elif stream.current().kind is TokenKind.FOR:
            if stream.experimental_loops:
                block.children.append(parse_for_statement(stream))
            else:
                stream.report(
                    "Use of 'for' requires --experimental-loops flag", "PAR012"
                )
        elif stream.current().kind is TokenKind.LBRACE:
            # Nested block
            block.children.append(parse_block(stream))
        else:
            old_index = stream.index
            block.children.append(parse_expression_statement(stream))
            # Guard: if stream didn't advance, force advance to avoid infinite loop
            if stream.index == old_index:
                stream.advance()
    stream.expect(TokenKind.RBRACE)
    block.end_span = stream.previous().end_offset
    return block


def parse_return_statement(stream: TokenStream) -> CSTNode:
    statement = CSTNode("ReturnStatement")
    statement.start_span = stream.current().start_offset
    stream.expect(TokenKind.RETURN)
    statement.children.append(parse_expression(stream))
    stream.match(TokenKind.SEMICOLON)
    statement.end_span = stream.previous().end_offset
    return statement


def parse_expression_statement(stream: TokenStream) -> CSTNode:
    statement = CSTNode("ExpressionStatement")
    statement.start_span = stream.current().start_offset
    statement.children.append(parse_expression(stream))
    stream.match(TokenKind.SEMICOLON)
    statement.end_span = stream.previous().end_offset
    return statement


def parse_for_statement(stream: TokenStream) -> CSTNode:
    statement = CSTNode("ForStatement")
    statement.start_span = stream.current().start_offset
    stream.expect(TokenKind.FOR)
    var_token = stream.current()
    if var_token.kind is not TokenKind.IDENTIFIER:
        stream.report("Expected identifier after 'for'", "PAR010")
        synchronize(stream)
        return statement
    stream.advance()
    var_node = CSTNode("Identifier", token=var_token)
    in_token = stream.current()
    if in_token.kind is not TokenKind.IDENTIFIER or in_token.value != "in":
        stream.report("Expected 'in' after loop variable", "PAR011")
        synchronize(stream)
        return statement
    stream.advance()
    statement.children.append(var_node)
    statement.children.append(parse_expression(stream))
    statement.children.append(parse_block(stream))
    statement.end_span = stream.previous().end_offset
    return statement


def parse_if_statement(stream: TokenStream) -> CSTNode:
    statement = CSTNode("IfStatement")
    statement.start_span = stream.current().start_offset
    stream.expect(TokenKind.IF)
    stream.expect(TokenKind.LPAREN)
    statement.children.append(parse_expression(stream))
    stream.expect(TokenKind.RPAREN)
    statement.children.append(parse_block(stream))
    if stream.match(TokenKind.ELSE):
        if stream.current().kind is TokenKind.IF:
            statement.children.append(parse_if_statement(stream))
        else:
            statement.children.append(parse_block(stream))
    statement.end_span = stream.previous().end_offset
    return statement

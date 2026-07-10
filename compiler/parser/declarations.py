from __future__ import annotations

from compiler.lexer import TokenKind
from compiler.parser.expressions import parse_expression, parse_identifier
from compiler.parser.nodes import CSTNode
from compiler.parser.token_stream import TokenStream


def parse_variable_declaration(stream: TokenStream) -> CSTNode:
    declaration = CSTNode("VariableDeclaration")
    declaration.start_span = stream.current().start_offset
    stream.expect(TokenKind.LET)
    declaration.children.append(parse_identifier(stream))
    stream.expect(TokenKind.ASSIGN)
    declaration.children.append(parse_expression(stream))
    stream.match(TokenKind.SEMICOLON)
    declaration.end_span = stream.previous().end_offset
    return declaration


def parse_function_declaration(stream: TokenStream) -> CSTNode:
    from compiler.parser.statements import parse_block

    declaration = CSTNode("FunctionDeclaration")
    declaration.start_span = stream.current().start_offset
    stream.expect(TokenKind.FN)
    declaration.children.append(parse_identifier(stream))
    stream.expect(TokenKind.LPAREN)
    declaration.children.append(parse_parameter_list(stream))
    stream.expect(TokenKind.RPAREN)
    declaration.children.append(parse_block(stream))
    declaration.end_span = stream.previous().end_offset
    return declaration


def parse_parameter_list(stream: TokenStream) -> CSTNode:
    parameters = CSTNode("ParameterList")
    parameters.start_span = stream.current().start_offset
    if stream.current().kind is TokenKind.IDENTIFIER:
        parameters.children.append(parse_identifier(stream))
        while stream.match(TokenKind.COMMA):
            parameters.children.append(parse_identifier(stream))
    parameters.end_span = stream.previous().end_offset
    return parameters

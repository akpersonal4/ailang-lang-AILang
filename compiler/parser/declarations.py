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

    # Detect nested function declarations
    if stream._nesting_depth > 0:
        from compiler.diagnostics import Diagnostic, LANG001_NESTED_FN, Severity

        fn_token = stream.current()
        diagnostic = Diagnostic(
            Severity.ERROR,
            LANG001_NESTED_FN,
            "Nested functions are not allowed in AILang. All functions must be at the top level.",
            fn_token.line,
            fn_token.column,
            stream.source_path,
        )
        if stream.reporter is not None:
            stream.reporter.report(diagnostic)

    declaration = CSTNode("FunctionDeclaration")
    declaration.start_span = stream.current().start_offset
    stream.expect(TokenKind.FN)
    declaration.children.append(parse_identifier(stream))
    stream.expect(TokenKind.LPAREN)
    declaration.children.append(parse_parameter_list(stream))
    stream.expect(TokenKind.RPAREN)
    stream._nesting_depth += 1
    declaration.children.append(parse_block(stream))
    stream._nesting_depth -= 1
    declaration.end_span = stream.previous().end_offset
    return declaration


def parse_parameter_list(stream: TokenStream) -> CSTNode:
    parameters = CSTNode("ParameterList")
    parameters.start_span = stream.current().start_offset

    def parse_one_parameter() -> CSTNode:
        ident = parse_identifier(stream)
        if stream.match(TokenKind.ASSIGN):
            param = CSTNode("DefaultParameter")
            param.start_span = ident.start_span
            param.children.append(ident)
            param.children.append(parse_expression(stream))
            param.end_span = stream.previous().end_offset
            return param
        return ident

    if stream.current().kind is TokenKind.IDENTIFIER:
        parameters.children.append(parse_one_parameter())
        while stream.match(TokenKind.COMMA):
            parameters.children.append(parse_one_parameter())
    parameters.end_span = stream.previous().end_offset
    return parameters

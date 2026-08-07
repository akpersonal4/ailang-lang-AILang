"""Statement-level parser functions for AILang."""

from __future__ import annotations

from compiler.diagnostics import Severity
from compiler.lexer import TokenKind
from compiler.parser.declarations import (
    parse_function_declaration,
    parse_variable_declaration,
)
from compiler.parser.expressions import parse_expression
from compiler.parser.nodes import CSTNode
from compiler.parser.recovery import synchronize
from compiler.parser.token_stream import TokenStream


def _skip_past_for_statement(stream: TokenStream) -> None:
    """Advance past a ``for`` statement that the parser is rejecting.

    Used after PAR012 (``for`` without --experimental-loops) so the outer
    statement loop does not loop forever on the for-header tokens and
    emit a cascade of spurious PAR001/PAR002 diagnostics. Scans forward
    until it finds the for-body's matching ``}`` (track brace depth) and
    consumes an optional trailing ``;``.
    """
    # Consume the ``for`` token itself.
    if stream.current().kind is TokenKind.FOR:
        stream.advance()
    # Walk forward until we close a single balanced ``{ ... }`` block
    # belonging to the for body. If no block is found, fall back to the
    # generic synchronize() so we still make forward progress.
    depth = 0
    while not stream.is_at_end():
        kind = stream.current().kind
        if kind is TokenKind.LBRACE:
            depth += 1
            stream.advance()
            continue
        if kind is TokenKind.RBRACE:
            if depth == 0:
                # Stray close-brace at top level; let synchronize handle it.
                break
            depth -= 1
            stream.advance()
            if depth == 0:
                # For body closed; consume optional trailing semicolon.
                if stream.current().kind is TokenKind.SEMICOLON:
                    stream.advance()
                return
            continue
        stream.advance()
    synchronize(stream)


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
                # Skip past the for header and body so the statement loop
                # makes forward progress instead of cascading PAR001/PAR002.
                _skip_past_for_statement(stream)
        elif (
            stream.current().kind is TokenKind.IDENTIFIER
            and stream.current().value == "while"
            and stream._token_at(stream.index + 1).kind is TokenKind.LPAREN
        ):
            # Detect "while(...)" — AILang has no while loops
            from compiler.diagnostics import Diagnostic, WHILE001_NO_WHILE_LOOPS

            cur = stream.current()
            diagnostic = Diagnostic(
                Severity.ERROR,
                WHILE001_NO_WHILE_LOOPS,
                "AILang has no while loops. Use recursion instead.",
                cur.line,
                cur.column,
                stream.source_path,
            )
            if stream.reporter is not None:
                stream.reporter.report(diagnostic)
            # In all cases, synchronize to avoid cascading errors
            from compiler.parser.recovery import synchronize as _sync

            _sync(stream)
        elif stream.current().kind is TokenKind.IMPORT:
            from compiler.diagnostics import (
                Diagnostic,
                LANG004_IMPORT_IN_FUNCTION,
            )

            cur = stream.current()
            diagnostic = Diagnostic(
                Severity.ERROR,
                LANG004_IMPORT_IN_FUNCTION,
                "Import statements are only allowed at the top level, not inside functions or blocks.",
                cur.line,
                cur.column,
                stream.source_path,
            )
            if stream.reporter is not None:
                stream.reporter.report(diagnostic)
            synchronize(stream)
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

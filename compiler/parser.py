from __future__ import annotations

from dataclasses import dataclass, field

from compiler.diagnostics import Diagnostic, DiagnosticReporter, ErrorCode, Severity
from compiler.lexer import Token, TokenKind


@dataclass
class CSTNode:
    kind: str
    children: list[CSTNode] = field(default_factory=list)
    token: Token | None = None
    start_span: int | None = None
    end_span: int | None = None

    def __str__(self) -> str:
        lines = [self.kind]
        for child in self.children:
            child_lines = str(child).splitlines()
            for child_line in child_lines:
                lines.append(f"  {child_line}")
        return "\n".join(lines)


class Parser:
    def __init__(
        self,
        tokens: list[Token],
        reporter: DiagnosticReporter | None = None,
    ) -> None:
        self.tokens = tokens
        self.reporter = reporter
        self.index = 0

    def current(self) -> Token:
        return self._token_at(self.index)

    def previous(self) -> Token:
        return self._token_at(self.index - 1)

    def peek(self) -> Token:
        return self.current()

    def advance(self) -> Token:
        token = self.current()
        if not self.is_at_end():
            self.index += 1
        return token

    def match(self, *kinds: TokenKind) -> bool:
        if self.current().kind in kinds:
            self.advance()
            return True
        return False

    def expect(self, kind: TokenKind) -> bool:
        if self.current().kind is kind:
            self.advance()
            return True
        self._report_error(f"Expected {kind.name}", "PAR001")
        return False

    def report(self, message: str, code: str = "PAR001") -> None:
        self._report_error(message, code)

    def synchronize(self) -> None:
        while not self.is_at_end():
            if self.current().kind in {TokenKind.SEMICOLON, TokenKind.RBRACE}:
                break
            self.advance()

    def is_at_end(self) -> bool:
        return self.current().kind is TokenKind.EOF

    def parse_program(self) -> CSTNode:
        program = CSTNode("Program")
        if self.tokens:
            program.start_span = self.tokens[0].start_offset
            program.end_span = self.tokens[-1].end_offset
        while not self.is_at_end():
            if self.current().kind is TokenKind.SEMICOLON:
                self.advance()
                continue
            if self.current().kind is TokenKind.LET:
                program.children.append(self.parse_variable_declaration())
            elif self.current().kind is TokenKind.FN:
                program.children.append(self.parse_function_declaration())
            elif self.current().kind is TokenKind.IF:
                program.children.append(self.parse_if_statement())
            else:
                self.report("Unexpected token in program")
                if self.current().kind is TokenKind.RBRACE:
                    self.advance()
                else:
                    self.synchronize()
        return program

    def parse_variable_declaration(self) -> CSTNode:
        declaration = CSTNode("VariableDeclaration")
        declaration.start_span = self.current().start_offset
        self.expect(TokenKind.LET)
        declaration.children.append(self.parse_identifier())
        self.expect(TokenKind.ASSIGN)
        declaration.children.append(self.parse_expression())
        self.expect(TokenKind.SEMICOLON)
        declaration.end_span = self.previous().end_offset
        return declaration

    def parse_function_declaration(self) -> CSTNode:
        declaration = CSTNode("FunctionDeclaration")
        declaration.start_span = self.current().start_offset
        self.expect(TokenKind.FN)
        declaration.children.append(self.parse_identifier())
        self.expect(TokenKind.LPAREN)
        declaration.children.append(self.parse_parameter_list())
        self.expect(TokenKind.RPAREN)
        declaration.children.append(self.parse_block())
        declaration.end_span = self.previous().end_offset
        return declaration

    def parse_parameter_list(self) -> CSTNode:
        parameters = CSTNode("ParameterList")
        parameters.start_span = self.current().start_offset
        if self.current().kind is TokenKind.IDENTIFIER:
            parameters.children.append(self.parse_identifier())
            while self.match(TokenKind.COMMA):
                parameters.children.append(self.parse_identifier())
        parameters.end_span = self.previous().end_offset
        return parameters

    def parse_block(self) -> CSTNode:
        block = CSTNode("Block")
        block.start_span = self.current().start_offset
        self.expect(TokenKind.LBRACE)
        while not self.is_at_end() and self.current().kind is not TokenKind.RBRACE:
            if self.current().kind is TokenKind.LET:
                block.children.append(self.parse_variable_declaration())
            elif self.current().kind is TokenKind.RETURN:
                block.children.append(self.parse_return_statement())
            elif self.current().kind is TokenKind.FN:
                block.children.append(self.parse_function_declaration())
            elif self.current().kind is TokenKind.IF:
                block.children.append(self.parse_if_statement())
            else:
                block.children.append(self.parse_expression_statement())
        self.expect(TokenKind.RBRACE)
        block.end_span = self.previous().end_offset
        return block

    def parse_if_statement(self) -> CSTNode:
        statement = CSTNode("IfStatement")
        statement.start_span = self.current().start_offset
        self.expect(TokenKind.IF)
        self.expect(TokenKind.LPAREN)
        statement.children.append(self.parse_expression())
        self.expect(TokenKind.RPAREN)
        statement.children.append(self.parse_block())
        if self.match(TokenKind.ELSE):
            if self.current().kind is TokenKind.IF:
                statement.children.append(self.parse_if_statement())
            else:
                statement.children.append(self.parse_block())
        statement.end_span = self.previous().end_offset
        return statement

    def parse_return_statement(self) -> CSTNode:
        statement = CSTNode("ReturnStatement")
        statement.start_span = self.current().start_offset
        self.expect(TokenKind.RETURN)
        statement.children.append(self.parse_expression())
        self.expect(TokenKind.SEMICOLON)
        statement.end_span = self.current().end_offset
        return statement

    def parse_expression_statement(self) -> CSTNode:
        statement = CSTNode("ExpressionStatement")
        statement.start_span = self.current().start_offset
        statement.children.append(self.parse_expression())
        self.expect(TokenKind.SEMICOLON)
        statement.end_span = self.current().end_offset
        return statement

    def parse_expression(self) -> CSTNode:
        return self.parse_assignment_expression()

    def parse_assignment_expression(self) -> CSTNode:
        left = self.parse_logical_or_expression()
        if self.match(TokenKind.ASSIGN):
            right = self.parse_assignment_expression()
            return CSTNode("AssignmentExpression", [left, right])
        return left

    def parse_logical_or_expression(self) -> CSTNode:
        left = self.parse_logical_and_expression()
        while self.current().kind is TokenKind.OROR:
            operator = self.advance()
            right = self.parse_logical_and_expression()
            left = CSTNode(
                "BinaryExpression",
                [left, right],
                operator,
                start_span=left.start_span,
                end_span=right.end_span,
            )
        return left

    def parse_logical_and_expression(self) -> CSTNode:
        left = self.parse_equality_expression()
        while self.current().kind is TokenKind.ANDAND:
            operator = self.advance()
            right = self.parse_equality_expression()
            left = CSTNode(
                "BinaryExpression",
                [left, right],
                operator,
                start_span=left.start_span,
                end_span=right.end_span,
            )
        return left

    def parse_equality_expression(self) -> CSTNode:
        left = self.parse_comparison_expression()
        while self.current().kind in {TokenKind.EQEQ, TokenKind.NEQ}:
            operator = self.advance()
            right = self.parse_comparison_expression()
            left = CSTNode(
                "BinaryExpression",
                [left, right],
                operator,
                start_span=left.start_span,
                end_span=right.end_span,
            )
        return left

    def parse_comparison_expression(self) -> CSTNode:
        left = self.parse_additive_expression()
        while self.current().kind in {
            TokenKind.LT,
            TokenKind.LTE,
            TokenKind.GT,
            TokenKind.GTE,
        }:
            operator = self.advance()
            right = self.parse_additive_expression()
            left = CSTNode(
                "BinaryExpression",
                [left, right],
                operator,
                start_span=left.start_span,
                end_span=right.end_span,
            )
        return left

    def parse_additive_expression(self) -> CSTNode:
        left = self.parse_multiplicative_expression()
        while self.current().kind in {TokenKind.PLUS, TokenKind.MINUS}:
            operator = self.advance()
            right = self.parse_multiplicative_expression()
            left = CSTNode(
                "BinaryExpression",
                [left, right],
                operator,
                start_span=left.start_span,
                end_span=right.end_span,
            )
        return left

    def parse_multiplicative_expression(self) -> CSTNode:
        left = self.parse_unary_expression()
        while self.current().kind in {
            TokenKind.STAR,
            TokenKind.SLASH,
            TokenKind.PERCENT,
        }:
            operator = self.advance()
            right = self.parse_unary_expression()
            left = CSTNode(
                "BinaryExpression",
                [left, right],
                operator,
                start_span=left.start_span,
                end_span=right.end_span,
            )
        return left

    def parse_unary_expression(self) -> CSTNode:
        if self.current().kind in {TokenKind.MINUS, TokenKind.BANG}:
            operator = self.advance()
            operand = self.parse_unary_expression()
            return CSTNode(
                "UnaryExpression",
                [operand],
                operator,
                start_span=operator.start_offset,
                end_span=operand.end_span,
            )
        return self.parse_postfix_expression()

    def parse_postfix_expression(self) -> CSTNode:
        expression = self.parse_primary_expression()
        while self.match(TokenKind.LPAREN):
            argument_list = self.parse_argument_list()
            self.expect(TokenKind.RPAREN)
            expression = CSTNode(
                "CallExpression",
                [expression, argument_list],
                start_span=expression.start_span,
                end_span=argument_list.end_span,
            )
        return expression

    def parse_argument_list(self) -> CSTNode:
        arguments = CSTNode("ArgumentList")
        arguments.start_span = self.current().start_offset
        if self.current().kind is not TokenKind.RPAREN:
            arguments.children.append(self.parse_expression())
            while self.match(TokenKind.COMMA):
                arguments.children.append(self.parse_expression())
        arguments.end_span = self.previous().end_offset
        return arguments

    def parse_primary_expression(self) -> CSTNode:
        if self.current().kind is TokenKind.NUMBER:
            token = self.advance()
            return CSTNode(
                "NumberLiteral",
                token=token,
                start_span=token.start_offset,
                end_span=token.end_offset,
            )
        if self.current().kind is TokenKind.STRING:
            token = self.advance()
            return CSTNode(
                "StringLiteral",
                token=token,
                start_span=token.start_offset,
                end_span=token.end_offset,
            )
        if self.current().kind is TokenKind.IDENTIFIER:
            return self.parse_identifier()
        if self.match(TokenKind.LPAREN):
            expression = self.parse_expression()
            self.expect(TokenKind.RPAREN)
            return expression
        self.report("Expected expression")
        return CSTNode("MissingExpression")

    def parse_identifier(self) -> CSTNode:
        token = self.current()
        if self.match(TokenKind.IDENTIFIER):
            return CSTNode(
                "Identifier",
                token=token,
                start_span=token.start_offset,
                end_span=token.end_offset,
            )
        self.report("Expected identifier")
        return CSTNode("Identifier")

    def _token_at(self, index: int) -> Token:
        if index >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[index]

    def _report_error(self, message: str, code: str) -> None:
        diagnostic = Diagnostic(
            Severity.ERROR,
            ErrorCode(code, message),
            message,
            self.current().line,
            self.current().column,
        )
        if self.reporter is not None:
            self.reporter.report(diagnostic)

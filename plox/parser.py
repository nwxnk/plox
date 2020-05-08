# coding: utf-8

from plox.exprs import *
from plox.stmts import *
from plox.token import Token, TokenType

class ParseError(Exception):
    pass

class Parser:
    __current = 0

    def __init__(self, plox, tokens):
        self.plox = plox
        self.tokens = tokens

    def parse(self):
        statements = []

        while not self.is_at_end():
            statements.append(self.declaration())

        return statements

    def is_at_end(self):
        return self.__current >= len(self.tokens) or \
            self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.__current]

    def previous(self):
        return self.tokens[self.__current - 1]

    def advance(self):
        self.__current += 1
        return self.previous()

    def check(self, t_type):
        if self.is_at_end():
            return False

        return self.peek().type == t_type

    def match(self, *types):
        for t_type in types:
            if self.check(t_type):
                self.advance(); return True

        return False

    def consume(self, t_type, message):
        if self.check(t_type):
            return self.advance()

        raise self.error(self.peek(), message)

    def error(self, token, message):
        self.plox.parse_error(token, message)
        return ParseError()

    def declaration(self):
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()

            return self.statement()
        except ParseError:
            self.synchronize()

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, 'expect variable name')
        init = self.expression() if self.match(TokenType.EQUAL) else None
        self.consume(TokenType.SEMICOLON, 'expect ";" after variable declaration')

        return VarStatement(name, init)

    def statement(self):
        if self.match(TokenType.IF): return self.if_statement()
        if self.match(TokenType.FOR): return self.for_statement()
        if self.match(TokenType.PRINT): return self.print_statement()
        if self.match(TokenType.WHILE): return self.while_statement()
        if self.match(TokenType.LEFT_BRACE): return self.block_statement()

        return self.expression_statement()

    def expression_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, 'expect ";" after value')
        return ExpressionStatement(value)

    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, 'expect "(" after for')

        if self.match(TokenType.SEMICOLON):
            init = None
        elif self.match(TokenType.VAR):
            init = self.var_declaration()
        else:
            init = self.expression_statement()

        condition = Literal(True) if self.check(TokenType.SEMICOLON) else self.expression()
        self.consume(TokenType.SEMICOLON, 'expect ";" after loop condition')

        increment = None if self.check(TokenType.RIGHT_PAREN) else self.expression()
        self.consume(TokenType.RIGHT_PAREN, "expect ')' after clauses")

        body = self.statement()

        if increment:
            body = BlockStatement([body, ExpressionStatement(increment)])

        body = WhileStatement(condition, body)

        if init:
            body = BlockStatement([init, body])

        return body

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, 'expect "(" after "if"')
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, 'expect ")" after if condition')

        else_branch = None
        then_branch = self.statement()

        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return IfStatement(condition, then_branch, else_branch)

    def print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, 'expect ";" after value')
        return PrintStatement(value)

    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, 'expect "(" after while')
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, 'expect ")" after while statement')

        return WhileStatement(condition, self.statement())

    def block_statement(self):
        statements = []

        while (not self.is_at_end()) and (not self.check(TokenType.RIGHT_BRACE)):
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, 'expect "}" after block')
        return BlockStatement(statements)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.or_expr()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value  = self.assignment()

            if type(expr) == Variable:
                return Assignment(expr.name, value)

            self.error(equals, 'invalid assignment target')

        return expr

    def or_expr(self):
        expr = self.and_expr()

        while self.match(TokenType.OR):
            expr = Logical(expr, self.previous(), self.and_expr())

        return expr

    def and_expr(self):
        expr = self.equality()

        while self.match(TokenType.AND):
            expr = Logical(expr, self.previous(), self.equality())

        return expr

    def equality(self):
        expr = self.comparsion()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            expr = Binary(expr, self.previous(), self.comparsion())

        return expr

    def comparsion(self):
        expr = self.addition()

        while self.match(TokenType.LESS, TokenType.GREATER, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            expr = Binary(expr, self.previous(), self.addition())

        return expr

    def addition(self):
        expr = self.multiplication()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            expr = Binary(expr, self.previous(), self.multiplication())

        return expr

    def multiplication(self):
        expr = self.unary()

        while self.match(TokenType.STAR, TokenType.SLASH):
            expr = Binary(expr, self.previous(), self.unary())

        return expr

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            return Unary(self.previous(), self.unary())

        return self.primary()

    def primary(self):
        if self.match(TokenType.NIL): return Literal(None)
        if self.match(TokenType.TRUE): return Literal(True)
        if self.match(TokenType.FALSE): return Literal(False) 

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, 'expected ")" after expression')
            return Grouping(expr)

        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

        raise self.error(self.peek(), 'expect expression')

    def synchronize(self):
        self.advance()

        type_list = [
            TokenType.IF,
            TokenType.VAR,
            TokenType.FOR,
            TokenType.FUN,
            TokenType.PRINT,
            TokenType.WHILE,
            TokenType.CLASS,
            TokenType.RETURN
        ]

        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            if self.peek().type in type_list:
                return

            self.advance()
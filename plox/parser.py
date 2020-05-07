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
            statements.append(self.statement())

        return statements

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

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

    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()

        return self.expression_statement()

    def print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, 'expect ";" after value')
        return PrintStatement(value)

    def expression_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, 'expect ";" after value')
        return ExpressionStatement(value)

    def expression(self):
        return self.equality()

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

        raise self.error(self.peek(), 'except expression')

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
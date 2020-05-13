# coding: utf-8

from plox.exprs import *
from plox.stmts import *
from plox.token import Token
from plox.types import TokenType
from plox.error import ParseError

class Parser:
    __current = 0

    def __init__(self, plox, tokens):
        self.plox = plox
        self.tokens = tokens

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

    def parse(self):
        statements = []

        while not self.is_at_end():
            statements.append(self.declaration())

        return [] if self.plox.error_occured else statements

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
        if self.match(TokenType.FUN): return self.function('function')
        if self.match(TokenType.PRINT): return self.print_statement()
        if self.match(TokenType.BREAK): return self.break_statement()
        if self.match(TokenType.WHILE): return self.while_statement()
        if self.match(TokenType.RETURN): return self.return_statement()
        if self.match(TokenType.CONTINUE): return self.continue_statement()
        if self.match(TokenType.LEFT_BRACE): return self.block_statement()

        return self.expression_statement()

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

        return self.call()

    def call(self):
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr); continue

            break

        return expr

    def finish_call(self, callee):
        arguments = []

        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())

            while self.match(TokenType.COMMA):
                arguments.append(self.expression())

        return Call(callee, self.consume(TokenType.RIGHT_PAREN, 'expect ")" after arguments'), arguments)

    def primary(self):
        if self.match(TokenType.NIL): return Literal(None)
        if self.match(TokenType.TRUE): return Literal(True)
        if self.match(TokenType.FALSE): return Literal(False) 

        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, 'expected ")" after expression')
            return Grouping(expr)

        raise self.error(self.peek(), 'expect expression')

    def expression_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, 'expect ";" after value')
        return ExpressionStatement(value)

    def function(self, kind):
        parameters = []

        name = self.consume(TokenType.IDENTIFIER, f'expect {kind} name')
        self.consume(TokenType.LEFT_PAREN, f'expect "(" after {kind} name)')

        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                parameters.append(
                    self.consume(TokenType.IDENTIFIER, 'expect parameter name'))

                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RIGHT_PAREN, 'expect ")" after parameters')
        self.advance()

        return FunctionStatement(name, parameters,  self.block_statement())

    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, 'expect "(" after for')

        if self.match(TokenType.SEMICOLON): init = None
        elif self.match(TokenType.VAR)    : init = self.var_declaration()
        else                              : init = self.expression_statement()

        condition = Literal(True) if self.check(TokenType.SEMICOLON) else self.expression()
        self.consume(TokenType.SEMICOLON, 'expect ";" after loop condition')

        increment = None if self.check(TokenType.RIGHT_PAREN) else self.expression()
        self.consume(TokenType.RIGHT_PAREN, "expect ')' after clauses")

        return BlockStatement([
            init, 
            WhileStatement(
                condition, 
                BlockStatement([
                    self.statement(), 
                    increment
                ])
            )
        ])

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

    def return_statement(self):
        value = None
        token = self.previous()

        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, 'expect ";" after return')
        return ReturnStatement(token, value)

    def break_statement(self):
        token = self.previous()
        self.consume(TokenType.SEMICOLON, 'expect ";" after break')

        return BreakStatement(token)

    def continue_statement(self):
        token = self.previous()
        self.consume(TokenType.SEMICOLON, 'expect ";" after continue')

        return ContinueStatement(token)

    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, 'expect "(" after while')
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, 'expect ")" after while statement')

        return WhileStatement(condition, self.statement())

    def block_statement(self):
        statements = []

        while (not self.check(TokenType.RIGHT_BRACE)) and (not self.is_at_end()):
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, 'expect "}" after block')
        return BlockStatement(statements)

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
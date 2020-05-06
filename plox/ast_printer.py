# coding: utf-8

from plox.exprs import *
from plox.token import Token, TokenType

class ASTPrinter:
    def __init__(self):
        pass

    def print(self, expr):
        return expr.accept(self)

    def visit_grouping(self, expr):
        return self.parenthesize('group', expr.expression)

    def visit_literal(self, expr):
        return "nil" if not expr.value else str(expr.value)

    def visit_unary(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.expression)

    def visit_binary(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def parenthesize(self, name, *exprs):
        return f"({name} {' '.join(map(lambda expr: expr.accept(self), exprs))})"

if __name__ == '__main__':
    binary_expr = Binary(
        Unary(
            Token(TokenType.MINUS, "-", None, 1),
            Literal(123)
        ),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(
            Literal(45.67)
        )
    )

    print(ASTPrinter().print(binary_expr))
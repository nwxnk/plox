# coding: utf-8

from numbers import Number
from plox.token import TokenType

class RuntimeError(Exception):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token

def is_truthy(object):
    return bool(object)

def stringify(object):
    if object is None:
        return 'nil'

    return {'True': 'true', 'False': 'false'}.get(str(object), str(object))

def check_number_operands(operator, *operands):
    if all(map(lambda o: isinstance(o, Number), operands)):
        return

    raise RuntimeError(operator, 'operands must be numbers')

class Interpreter:
    def __init__(self, plox):
        self.plox = plox

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as error:
            self.plox.runtime_error(error)

    def evaluate(self, expr):
        return expr.accept(self)

    def execute(self, stmt):
        stmt.accept(self)
        
    def visit_literal(self, expr):
        return expr.value

    def visit_grouping(self, expr):
        return self.evaluate(expr.expression)

    def visit_unary(self, expr):
        right = self.evaluate(expr.expression)

        if expr.operator.type == TokenType.MINUS:
            check_number_operands(expr.operator, right)
            return -1 * right

        elif expr.operator.type == TokenType.BANG:
            return not is_truthy(right)

        return None

    def visit_binary(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        t_type = expr.operator.type

        if t_type not in [TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL, TokenType.PLUS]:
            check_number_operands(expr.operator, left, right)

        if t_type is TokenType.EQUAL_EQUAL:
            return left == right

        elif t_type is TokenType.BANG_EQUAL:
            return not (left == right)

        elif t_type is TokenType.LESS:
            return left < right

        elif t_type is TokenType.GREATER:
            return left > right

        elif t_type is TokenType.LESS_EQUAL:
            return left <= right

        elif t_type is TokenType.GREATER_EQUAL:
            return left >= right

        elif t_type is TokenType.STAR:
            return left * right

        elif t_type is TokenType.SLASH:
            return left / right

        elif t_type is TokenType.MINUS:
            return left - right

        elif t_type is TokenType.PLUS:
            try:
                return left + right
            except TypeError:
                raise RuntimeError(expr.operator, 'operands must be two numbers or strings')

        return None

    def visit_expression_statement(self, stmt):
        self.evaluate(stmt.expression)

    def visit_print_statement(self, stmt):
        print(stringify(self.evaluate(stmt.expression)))
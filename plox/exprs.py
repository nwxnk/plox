# coding: utf-8

__all__ = ('Expression', 'Variable', 'Literal', 'Grouping', 'Unary', 'Binary')

class Expression:
    pass

class Variable(Expression):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_variable(self)

class Literal(Expression):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal(self)

class Grouping(Expression):
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_grouping(self)

class Unary(Expression):
    def __init__(self, operator, expression):
        self.operator = operator
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_unary(self)

class Binary(Expression):
    def __init__(self, l_expr, operator, r_expr):
        self.left = l_expr
        self.right = r_expr
        self.operator = operator

    def accept(self, visitor):
        return visitor.visit_binary(self)
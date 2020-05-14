# coding: utf-8

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

class This(Expression):
    def __init__(self, token):
        self.token = token

    def accept(self, visitor):
        return visitor.visit_this(self)

class Get(Expression):
    def __init__(self, object, name):
        self.name = name
        self.object = object

    def accept(self, visitor):
        return visitor.visit_get(self)

class Set(Expression):
    def __init__(self, object, name, value):
        self.name = name
        self.value = value
        self.object = object

    def accept(self, visitor):
        return visitor.visit_set(self)

class Unary(Expression):
    def __init__(self, operator, expression):
        self.operator = operator
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_unary(self)

class Assignment(Expression):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_assignment(self)

class Call(Expression):
    def __init__(self, callee, paren, arguments):
        self.paren = paren
        self.callee = callee
        self.arguments = arguments

    def accept(self, visitor):
        return visitor.visit_call(self)

class Logical(Expression):
    def __init__(self, left, operator, right):
        self.left = left
        self.right = right
        self.operator = operator

    def accept(self, visitor):
        return visitor.visit_logical(self)

class Binary(Expression):
    def __init__(self, l_expr, operator, r_expr):
        self.left = l_expr
        self.right = r_expr
        self.operator = operator

    def accept(self, visitor):
        return visitor.visit_binary(self)
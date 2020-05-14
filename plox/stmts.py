# coding: utf-8

class Statement:
    pass

class PrintStatement(Statement):
    def __init__(self, expr):
        self.expression = expr

    def accept(self, visitor):
        visitor.visit_print_statement(self)

class ExpressionStatement(Statement):
    def __init__(self, expr):
        self.expression = expr

    def accept(self, visitor):
        visitor.visit_expression_statement(self)

class BreakStatement(Statement):
    def __init__(self, token):
        self.token = token

    def accept(self, visitor):
        visitor.visit_break_statement(self)

class ContinueStatement(Statement):
    def __init__(self, token):
        self.token = token

    def accept(self, visitor):
        visitor.visit_continue_statement(self)

class BlockStatement(Statement):
    def __init__(self, statements):
        self.statements = statements

    def accept(self, visitor):
        visitor.visit_block_statement(self)

class ReturnStatement(Statement):
    def __init__(self, token, value):
        self.value = value
        self.token = token

    def accept(self, visitor):
        visitor.visit_return_statement(self)

class WhileStatement(Statement):
    def __init__(self, condition, statement):
        self.condition = condition
        self.statement = statement

    def accept(self, visitor):
        visitor.visit_while_statement(self)

class VarStatement(Statement):
    def __init__(self, name, expr):
        self.name = name
        self.initializer = expr

    def accept(self, visitor):
        visitor.visit_var_statement(self)

class ClassStatement(Statement):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def accept(self, visitor):
        visitor.visit_class_statement(self)

class FunctionStatement(Statement):
    def __init__(self, name, params, body):
        self.name = name
        self.body = body
        self.params = params

    def accept(self, visitor):
        visitor.visit_function_statement(self)

class IfStatement(Statement):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor):
        visitor.visit_if_statement(self)
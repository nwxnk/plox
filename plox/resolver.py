# coding: utf-8

class Resolver:
    __scopes = []

    def __init__(self, plox, interpreter):
        self.plox = plox
        self.interpreter = interpreter

    def begin_scope(self):
        self.__scopes.append({})

    def end_scope(self):
        self.__scopes.pop()

    def declare(self, name):
        if not self.__scopes:
            return None
        
        if name.lexeme in self.__scopes[-1]:
            self.plox.resolve_error(name, 'variable with this name already declared in this scope')

        self.__scopes[-1][name.lexeme] = False

    def define(self, name):
        if self.__scopes:
            self.__scopes[-1][name.lexeme] = True

    def resolve(self, *args):
        for arg in args:
            if arg: arg.accept(self)

    def resolve_local(self, expr, name):
        for i in range(0, len(self.__scopes))[::-1]:
            if name.lexeme in self.__scopes[i]:
                self.interpreter.resolve(expr, len(self.__scopes) - 1 - i)

    def resolve_function(self, function):
        self.begin_scope()

        for param in function.params:
            self.declare(param)
            self.define (param)

        self.resolve(function.body)
        self.end_scope()

    def visit_literal(self, expr):
        return None

    def visit_grouping(self, expr):
        self.resolve(expr.expression)

    def visit_unary(self, expr):
        self.resolve(expr.right)

    def visit_assignment(self, expr):
        self.resolve(expr.value)
        self.resolve_local(expr.name, expr)

    def visit_binary(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_logical(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_call(self, expr):
        self.resolve(expr.callee)

        for arg in expr.arguments:
            self.resolve(arg)

    def visit_variable(self, expr):        
        if self.__scopes and (self.__scopes[-1].get(expr.name.lexeme, None) == False):
            self.plox.resolve_error(expr.name, 'can not read local variable in it\'s own initializer')

        self.resolve_local(expr, expr.name)

    def visit_expression_statement(self, stmt):
        self.resolve(stmt.expression)

    def visit_print_statement(self, stmt):
        self.resolve(stmt.expression)

    def visit_return_statement(self, stmt):
        return self.resolve(stmt.value) if stmt.value else None

    def visit_while_statement(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visit_block_statement(self, stmt):
        self.begin_scope()
        self.resolve(*stmt.statements)
        self.end_scope()

    def visit_var_statement(self, stmt):
        self.declare(stmt.name)
        self.resolve(stmt.initializer)
        self.define (stmt.name)

    def visit_function_statement(self, stmt):
        self.declare(stmt.name)
        self.define (stmt.name)
        self.resolve_function(stmt)

    def visit_if_statement(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        self.resolve(stmt.else_branch)
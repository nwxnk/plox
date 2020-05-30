# coding: utf-8

from plox.types import ClassType
from plox.types import FunctionType

class Resolver:
    __scopes = []
    __currcl = ClassType.NONE
    __currfn = FunctionType.NONE

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

    def resolve_function(self, function, fn_type):
        enclosing_fn = self.__currfn
        self.__currfn = fn_type

        self.begin_scope()

        for param in function.params:
            self.declare(param)
            self.define (param)

        self.resolve(*function.body.statements)
        self.end_scope()

        self.__currfn = enclosing_fn

    def visit_literal(self, expr):
        return None

    def visit_super(self, expr):
        message = {
            ClassType.NONE : 'can not use "super" outside of a class',
            ClassType.CLASS: 'can not use "super" in a class with no superclass'
        }.get(self.__currcl, None)

        if message:
            self.plox.resolve_error(expr.token, message)

        self.resolve_local(expr, expr.token)

    def visit_grouping(self, expr):
        self.resolve(expr.expression)

    def visit_unary(self, expr):
        self.resolve(expr.expression)

    def visit_get(self, expr):
        self.resolve(expr.object)

    def visit_assignment(self, expr):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_binary(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_logical(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_set(self, expr):
        self.resolve(expr.value)
        self.resolve(expr.object)

    def visit_call(self, expr):
        self.resolve(expr.callee)

        for arg in expr.arguments:
            self.resolve(arg)

    def visit_this(self, expr):
        if self.__currfn == ClassType.NONE:
            self.plox.resolve_error(expr.token, 'can not use "this" outside of a class')

        self.resolve_local(expr, expr.token)

    def visit_expression_statement(self, stmt):
        self.resolve(stmt.expression)

    def visit_break_statement(self, stmt):
        self.resolve_local(stmt, stmt.token)

    def visit_print_statement(self, stmt):
        self.resolve(stmt.expression)

    def visit_while_statement(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.statement)

    def visit_block_statement(self, stmt):
        self.begin_scope()
        self.resolve(*stmt.statements)
        self.end_scope()

    def visit_var_statement(self, stmt):
        self.declare(stmt.name)
        self.resolve(stmt.initializer)
        self.define (stmt.name)

    def visit_if_statement(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        self.resolve(stmt.else_branch)

    def visit_function_statement(self, stmt):
        self.declare(stmt.name)
        self.define (stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_variable(self, expr):        
        if self.__scopes and (self.__scopes[-1].get(expr.name.lexeme, None) == False):
            self.plox.resolve_error(expr.name, 'can not read local variable in it\'s own initializer')

        self.resolve_local(expr, expr.name)

    def visit_return_statement(self, stmt):
        if self.__currfn == FunctionType.NONE:
            self.plox.resolve_error(stmt.token, 'can not return from top-level code')

        if stmt.value and self.__currfn == FunctionType.INITIALIZER:
            self.plox.resolve_error(stmt.token, 'can not return a value from an initializer')

        self.resolve(stmt.value)

    def visit_class_statement(self, stmt):
        enclosing_cl = self.__currcl
        self.__currcl = ClassType.CLASS

        self.declare(stmt.name)
        self.define (stmt.name)

        if stmt.superclass and stmt.name.lexeme == stmt.superclass.name.lexeme:
            self.plox.resolve_error(stmt.superclass.name, 'a class can not inherit from itself')

        if stmt.superclass:
            self.__currcl = ClassType.SUBCLASS

            self.resolve(stmt.superclass)
            self.begin_scope()
            self.__scopes[-1]['super'] = True

        self.begin_scope()
        self.__scopes[-1]['this'] = True

        for method in stmt.methods:
            self.resolve_function(
                method,
                FunctionType.INITIALIZER if method.name.lexeme == 'init' else FunctionType.METHOD
            )

        self.end_scope()
        self.__currcl = ClassType.NONE

        if stmt.superclass:
            self.end_scope()
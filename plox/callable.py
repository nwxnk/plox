# coding: utf-8

from plox.error import ReturnException
from plox.environment import Environment

class LoxCallable:
    def call(self, interpreter, arguments):
        pass

    def arity(self):
        pass

class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure):
        self.closure = closure
        self.declaration = declaration

    def __str__(self):
        return f'<fn {self.declaration.name.lexeme}>'

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)

        for (param, val) in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, val)

        try:
            interpreter.execute_block(self.declaration.body.statements, environment)
        except ReturnException as ret:
            return ret.value
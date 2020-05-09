# coding: utf-8

from plox.environment import Environment

class LoxCallable:
    def call(self, interpreter, arguments):
        pass

    def arity(self):
        pass

class LoxFunction(LoxCallable):
    def __init__(self, declaration):
        self.declaration = declaration

    def __str__(self):
        return f'<fn {self.declaration.name.lexeme}>'

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, arguments):
        environment = Environment(interpreter.globals)

        for (param, val) in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, val)

        interpreter.execute_block(self.declaration.body.statements, environment)
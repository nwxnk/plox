# coding: utf-8

from plox.error import RuntimeError
from plox.error import ReturnException
from plox.environment import Environment

class LoxCallable:
    def arity(self):
        pass

    def call(self, interpreter, arguments):
        pass

class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure, initializer=False):
        self.closure = closure
        self.declaration = declaration
        self.initializer = initializer

    def __str__(self):
        return '<fn {}({})>'.format(
            self.declaration.name.lexeme,
            ', '.join(p.lexeme for p in self.declaration.params)
        )

    def arity(self):
        return len(self.declaration.params)

    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define('this', instance)

        return LoxFunction(self.declaration, environment, self.initializer)

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)

        for (param, val) in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, val)

        try:
            interpreter.execute_block(self.declaration.body.statements, environment)
        except ReturnException as ret:
            if not self.initializer:
                return ret.value

        if self.initializer:
            return self.closure.get_at(0, 'this')

class LoxInstance:
    def __init__(self, lclass):
        self.fields = {}
        self.lclass = lclass

    def __str__(self):
        return f'<class instance "{self.lclass.name}">'

    def set(self, name, value):
        self.fields[name.lexeme] = value

    def get(self, name):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        if (method := self.lclass.find_method(name.lexeme)):
            return method.bind(self)

        raise RuntimeError(name, f'undefined property {name.lexeme}')

class LoxClass(LoxCallable):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def __str__(self):
        return f'<class "{self.name}">'

    def find_method(self, name):
        return self.methods.get(name, None)

    def arity(self):
        if (initializer := self.find_method('init')):
            return initializer.arity()

        return 0

    def call(self, interpreter, arguments):
        instance = LoxInstance(self)

        if (initializer := self.find_method('init')):
            initializer.bind(instance).call(interpreter, arguments)

        return instance
# coding: utf-8

from plox.error import RuntimeError

class Environment:
    def __init__(self, enclosing=None):
        self.__values  = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.__values[name] = value

    def get(self, name):
        try:
            return self.__values[name.lexeme]
        except KeyError:

            if self.enclosing:
                return self.enclosing.get(name)

            raise RuntimeError(name, f'undefined variable "{name.lexeme}"')

    def assign(self, name, value):
        if name.lexeme in self.__values:
            self.__values[name.lexeme] = value; return

        if self.enclosing:
            self.enclosing.assign(name, value); return

        raise RuntimeError(name, f'undefined variable "{name.lexeme}"')
# coding: utf-8

from plox.error import RuntimeError

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name] = value

    def get_at(self, distance, name):
        return self.ancestor(distance).values[name]

    def assign_at(self, distance, name, value):
        self.ancestor(distance).values[name.lexeme] = value

    def ancestor(self, distance):
        env = self

        for _ in range(distance):
            env = env.enclosing

        return env

    def get(self, name):
        try:
            return self.values[name.lexeme]
        except KeyError:

            if self.enclosing:
                return self.enclosing.get(name)

            raise RuntimeError(name, f'undefined variable "{name.lexeme}"')

    def assign(self, name, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value; return

        if self.enclosing:
            self.enclosing.assign(name, value); return

        raise RuntimeError(name, f'undefined variable "{name.lexeme}"')
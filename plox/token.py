# coding: utf-8

class Token:
    def __init__(self, type, lexeme, literal, line):
        self.line = line
        self.type = type
        self.lexeme = lexeme
        self.literal = literal

    def __str__(self):
        return f'Token({self.type.name}, {self.lexeme}, {self.literal})'

    def __repr__(self):
        return self.__str__()
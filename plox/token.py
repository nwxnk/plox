# coding: utf-8

from enum import Enum

TokenType = Enum(
    'TokenType', 
    '''
    IDENTIFIER STRING NUMBER

    BANG BANG_EQUAL EQUAL EQUAL_EQUAL
    GREATER GREATER_EQUAL LESS LESS_EQUAL

    COMMA DOT MINUS PLUS SEMICOLON SLASH STAR
    LEFT_PAREN RIGHT_PAREN LEFT_BRACE RIGHT_BRACE

    EOF IF CLASS ELSE TRUE BREAK FUN FOR AND OR VAR
    CONTINUE SUPER PRINT FALSE RETURN NIL WHILE THIS
    '''
)

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
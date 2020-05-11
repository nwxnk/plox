# coding: utf-8

from enum import auto, Enum

class TokenType(Enum):
    EOF      = auto()
    AND      = auto()
    CLASS    = auto()
    ELSE     = auto()
    FALSE    = auto()
    FUN      = auto()
    FOR      = auto()
    IF       = auto()
    NIL      = auto()
    OR       = auto()
    PRINT    = auto()
    BREAK    = auto()
    RETURN   = auto()
    CONTINUE = auto()
    SUPER    = auto()
    THIS     = auto()
    TRUE     = auto()
    VAR      = auto()
    WHILE    = auto()

    IDENTIFIER = auto()
    STRING     = auto()
    NUMBER     = auto()

    LEFT_PAREN  = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE  = auto()
    RIGHT_BRACE = auto()
    COMMA       = auto()
    DOT         = auto()
    MINUS       = auto()
    PLUS        = auto()
    SEMICOLON   = auto()
    SLASH       = auto()
    STAR        = auto()

    BANG          = auto()
    BANG_EQUAL    = auto()
    EQUAL         = auto()
    EQUAL_EQUAL   = auto()
    GREATER       = auto()
    GREATER_EQUAL = auto()
    LESS          = auto()
    LESS_EQUAL    = auto()

class Token:
    def __init__(self, type, lexeme, literal, line):
        self.line = line
        self.type = type
        self.lexeme = lexeme
        self.literal = literal

    def __str__(self):
        return f'Token({self.type.name} {self.lexeme} {self.literal})'

    def __repr__(self):
        return self.__str__()
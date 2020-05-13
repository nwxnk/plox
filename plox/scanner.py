# coding: utf-8

from plox.token import Token
from plox.types import TokenType

class Scanner:
    __line    = 1
    __start   = 0
    __current = 0

    def __init__(self, plox, source):
        self.plox = plox
        self.tokens = []
        self.source = source

        self._reserved_words = {
            'if'      : TokenType.IF,
            'or'      : TokenType.OR,
            'and'     : TokenType.AND,
            'nil'     : TokenType.NIL,
            'fun'     : TokenType.FUN,
            'for'     : TokenType.FOR,
            'var'     : TokenType.VAR,
            'true'    : TokenType.TRUE,
            'this'    : TokenType.THIS,
            'else'    : TokenType.ELSE,
            'break'   : TokenType.BREAK,
            'print'   : TokenType.PRINT,
            'super'   : TokenType.SUPER,
            'false'   : TokenType.FALSE,
            'while'   : TokenType.WHILE,
            'class'   : TokenType.CLASS,
            'return'  : TokenType.RETURN,
            'continue': TokenType.CONTINUE
        }

        self._token_dict = {
            ' ' : lambda: None,
            '\r': lambda: None,
            '\t': lambda: None,

            '"' : lambda: self._string('"'),
            '\'': lambda: self._string('\''),
            '\n': lambda: self.advance_line(),
            '/' : lambda: self._slash_tokens(),

            '(': lambda: self.add_token(TokenType.LEFT_PAREN),
            ')': lambda: self.add_token(TokenType.RIGHT_PAREN),
            '{': lambda: self.add_token(TokenType.LEFT_BRACE),
            '}': lambda: self.add_token(TokenType.RIGHT_BRACE),
            '.': lambda: self.add_token(TokenType.DOT),
            ',': lambda: self.add_token(TokenType.COMMA),
            '-': lambda: self.add_token(TokenType.MINUS),
            '+': lambda: self.add_token(TokenType.PLUS),
            ';': lambda: self.add_token(TokenType.SEMICOLON),
            '*': lambda: self.add_token(TokenType.STAR),

            '!': lambda: self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG),
            '=': lambda: self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL),
            '<': lambda: self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS),
            '>': lambda: self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
        }

    def default_case(self):
        char = self.source[self.__current - 1]

        if char.isdigit():
            self._number(); return

        elif char.isalpha():
            self._identifier(); return

        self.plox.scan_error(self.__line, f'{char} unexpected character')

    def scan_tokens(self):
        while not self.is_at_end():
            self.__start = self.__current
            self._token_dict.get(self.advance(), lambda: self.default_case())()

        return self.tokens + [Token(TokenType.EOF, '', None, self.__line)]

    def is_at_end(self, n=0):
        return self.__current + n >= len(self.source)

    def advance(self):
        self.__current += 1
        return self.source[self.__current - 1]

    def advance_line(self):
        self.__line += 1

    def peek(self, n=1):
        if self.is_at_end(n - 1):
            return '\0'

        return self.source[self.__current + n - 1]

    def match(self, expected):
        if self.is_at_end() or expected != self.source[self.__current]:
            return False

        self.advance(); return True

    def add_token(self, token_type, literal=None):
        self.tokens.append(
            Token(token_type, self.source[self.__start:self.__current], literal, self.__line))

    def _slash_tokens(self):
        if not self.match('/'):
            self.add_token(TokenType.SLASH); return

        while self.peek() != '\n' and not self.is_at_end():
            self.advance()

    def _string(self, quote):
        while self.peek() != quote and not self.is_at_end():
            if self.peek() == '\n':
                self.advance_line()

            self.advance()

        if self.is_at_end():
            self.plox.scan_error(self.__line, 'unterminated string'); return

        self.advance()
        self.add_token(TokenType.STRING, self.source[self.__start + 1:self.__current - 1])

    def _number(self):
        while self.peek().isdigit():
            self.advance()

        if self.peek() == '.' and self.peek(2).isdigit():
            self.advance()

            while self.peek().isdigit():
                self.advance()

        number = self.source[self.__start:self.__current]
        number = int(number) if '.' not in number else float(number)
        
        self.add_token(TokenType.NUMBER, number)

    def _identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()

        self.add_token(
            self._reserved_words.get(self.source[self.__start:self.__current], TokenType.IDENTIFIER))
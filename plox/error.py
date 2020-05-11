# coding: utf-8

class ParseError(Exception):
    pass

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class RuntimeError(Exception):
    def __init__(self, token, message):
        self.token = token
        self.message = message
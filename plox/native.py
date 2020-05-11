# coding: utf-8

import numbers
import time, math

from plox.callable import LoxCallable

class Abs(LoxCallable):
    def arity(self):
        return 1

    def call(self, interpreter, arguments):
        return abs(arguments[0])

class Pow(LoxCallable):
    def arity(self):
        return 2

    def call(self, interpreter, arguments):
        return pow(*arguments)

class Exit(LoxCallable):
    def arity(self):
        return 1

    def call(self, interpreter, arguments):
        exit(arguments[0])

class Clock(LoxCallable):
    def arity(self):
        return 0

    def call(self, interpreter, arguments):
        return time.time()

class Input(LoxCallable):
    def arity(self):
        return 1

    def call(self, interpreter, arguments):
        value = input(arguments[0])

        try   : return float(value)
        except: return value

def init_functions(interpreter):
    functions = {
        'abs'  : Abs(),
        'pow'  : Pow(),
        'exit' : Exit(),
        'clock': Clock(),
        'input': Input()
    }

    for name, fn in functions.items():
        interpreter.globals.define(name, fn)

    return interpreter
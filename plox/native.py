# coding: utf-8

import time
import math

from plox.callable import LoxCallable

class Pow(LoxCallable):
    def arity(self):
        return 2

    def call(self, interpreter, arguments):
        return pow(*arguments)

class Clock(LoxCallable):
    def arity(self):
        return 0

    def call(self, interpreter, arguments):
        return time.time()

def init_functions(interpreter):
    functions = {
        'pow'  : Pow(),
        'clock': Clock()
    }

    for name, fn in functions.items():
        interpreter.globals.define(name, fn)

    return interpreter
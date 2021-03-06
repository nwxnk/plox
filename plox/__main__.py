# coding: utf-8

import sys
import readline

from plox.parser import Parser
from plox.scanner import Scanner
from plox.resolver import Resolver
from plox.interpreter import Interpreter

from plox.native import init_functions

def get_input():
    braces = 1
    source = input('>>> ').rstrip()

    if len(source) == 0 or source[-1] != '{':
        return source

    while braces != 0:
        if (value := input('... ').rstrip()):
            source += value
            braces += {'{': 1, '}': -1}.get(source[-1], 0)

    return source

class PLox:
    def __init__(self):
        self.interpreter = init_functions(Interpreter(self))
        self.error_occured = False
        self.runtime_error_occured = False

    def run(self, source):
        token_list = Scanner(self, source).scan_tokens()
        statements = Parser(self, token_list).parse()

        if not self.error_occured:
            resolver = Resolver(self, self.interpreter)
            resolver.resolve(*statements)

        if not self.error_occured:
            self.interpreter.interpret(statements)

    def run_prompt(self):
        while True:
            try:
                self.run(get_input())
                self.error_occured = False
                self.runtime_error_occured = False
            except KeyboardInterrupt:
                print()

    def run_file(self, file_name):
        with open(file_name, 'r') as f:
            self.run(f.read())

        if self.error_occured:
            sys.exit(65)

        if self.runtime_error_occured:
            sys.exit(70)

    def scan_error(self, line, message):
        self.report(line, '\b', message)
        self.error_occured = True

    def parse_error(self, token, message):
        where = 'at end' if token.type.name == 'EOF' else f"at '{token.lexeme}'"
        self.report(token.line, where, message)
        self.error_occured = True

    def resolve_error(self, token, message):
        self.report(token.line, '\b', message)
        self.error_occured = True

    def runtime_error(self, error):
        self.report(error.token.line, '\b', f'"{error.token.lexeme}" {error.message}')
        self.runtime_error_occured = True

    def report(self, line, where, message, ofile=sys.stderr):
        print(f'line {line}: {where} {message}', file=ofile)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        PLox().run_prompt()

    PLox().run_file(sys.argv[1])
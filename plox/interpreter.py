# coding: utf-8

from numbers import Number

from plox.types import TokenType
from plox.environment import Environment

from plox.error import (
    ReturnException, BreakException, 
    RuntimeError, ContinueException
)

from plox.callable import LoxClass
from plox.callable import LoxInstance
from plox.callable import LoxCallable
from plox.callable import LoxFunction

def is_truthy(object):
    return bool(object)

def stringify(object):
    if object is None:
        return 'nil'

    if type(object) is bool:
        return str(object).lower()

    return str(object)

def check_number_operands(operator, *operands):
    if all(map(lambda o: isinstance(o, Number), operands)):
        return

    raise RuntimeError(operator, 'operands must be numbers')

class Interpreter:
    def __init__(self, plox):
        self.plox = plox
        self.locals = {}
        self.globals = Environment()
        self.environment = self.globals

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)

        except RuntimeError as error:
            self.plox.runtime_error(error)

    def resolve(self, expr, depth):
        self.locals[expr] = depth

    def look_up_variable(self, name, expr):
        if (distance := self.locals.get(expr, None)) is not None:
            return self.environment.get_at(distance, name.lexeme)

        return self.globals.get(name)

    def evaluate(self, expr):
        if expr: return expr.accept(self)

    def execute(self, stmt):
        if stmt: stmt.accept(self)

    def execute_block(self, statements, environment):
        previous = self.environment

        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)

        finally:
            self.environment = previous
        
    def visit_literal(self, expr):
        return expr.value

    def visit_grouping(self, expr):
        return self.evaluate(expr.expression)

    def visit_this(self, expr):
        return self.look_up_variable(expr.token, expr)

    def visit_variable(self, expr):
        return self.look_up_variable(expr.name, expr)

    def visit_unary(self, expr):
        right = self.evaluate(expr.expression)

        if expr.operator.type == TokenType.MINUS:
            check_number_operands(expr.operator, right)
            return -1 * right

        elif expr.operator.type == TokenType.BANG:
            return not is_truthy(right)

        return None

    def visit_assignment(self, expr):
        value = self.evaluate(expr.value)

        if (distance := self.locals.get(expr, None)) is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)

        return value

    def visit_logical(self, expr):
        left = self.evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if is_truthy(left):
                return left
        else:
            if not is_truthy(left):
                return left

        return self.evaluate(expr.right)

    def visit_get(self, expr):
        object = self.evaluate(expr.object)

        if isinstance(object, LoxInstance):
            return object.get(expr.name)

        raise RuntimeError(expr.name, 'only instances have properties')

    def visit_set(self, expr):
        object = self.evaluate(expr.object)

        if not isinstance(object, LoxInstance):
            raise RuntimeError(expr.name, 'only instances have fields')

        value = self.evaluate(expr.value)
        object.set(expr.name, value)

        return value

    def visit_super(self, expr):
        distance = self.locals[expr]

        superclass = self.environment.get_at(distance, 'super')
        object     = self.environment.get_at(distance - 1, 'this')
        method     = superclass.find_method(expr.method.lexeme)

        if not method:
            raise RuntimeError(expr.method, f'undefined method "{expr.method.lexeme}"')

        return method.bind(object)

    def visit_call(self, expr):
        function  = self.evaluate(expr.callee)
        arguments = [self.evaluate(arg) for arg in expr.arguments]

        if not isinstance(function, LoxCallable):
            raise RuntimeError(expr.paren, 'can only call functions and classes')

        if len(arguments) != function.arity():
            raise RuntimeError(
                expr.paren, f'expected {function.arity()} arguments but got {len(arguments)}')

        return function.call(self, arguments)

    def _plus(self, left, right, operator):
        try:
            if isinstance(left, str) or isinstance(right, str):
                return f'{left}{right}'

            return left + right
        except TypeError:
            raise RuntimeError(operator, 'operands must be numbers or strings')

    def visit_binary(self, expr):
        left   = self.evaluate(expr.left)
        right  = self.evaluate(expr.right)

        if expr.operator.type not in [TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL, TokenType.PLUS]:
            check_number_operands(expr.operator, left, right)

        return {
            TokenType.LESS         : lambda: left < right,
            TokenType.GREATER      : lambda: left > right,
            TokenType.STAR         : lambda: left * right,
            TokenType.SLASH        : lambda: left / right,
            TokenType.MINUS        : lambda: left - right,
            TokenType.EQUAL_EQUAL  : lambda: left == right,
            TokenType.LESS_EQUAL   : lambda: left <= right,
            TokenType.GREATER_EQUAL: lambda: left >= right,
            TokenType.BANG_EQUAL   : lambda: not (left == right),
            TokenType.PLUS         : lambda: self._plus(left, right, expr.operator)
        }.get(expr.operator.type, lambda: None)()

    def visit_expression_statement(self, stmt):
        self.evaluate(stmt.expression)

    def visit_function_statement(self, stmt):
        self.environment.define(stmt.name.lexeme, LoxFunction(stmt, self.environment))

    def visit_print_statement(self, stmt):
        print(stringify(self.evaluate(stmt.expression)))

    def visit_break_statement(self, stmt):
        raise BreakException()

    def visit_continue_statement(self, stmt):
        raise ContinueException()

    def visit_return_statement(self, stmt):
        raise ReturnException(self.evaluate(stmt.value))

    def visit_var_statement(self, stmt):
        value = None

        if stmt.initializer:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

    def visit_block_statement(self, stmt):
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_if_statement(self, stmt):
        if is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)

        elif stmt.else_branch:
            self.execute(stmt.else_branch)

    def visit_while_statement(self, stmt):
        while is_truthy(self.evaluate(stmt.condition)):
            try:
                self.execute(stmt.statement)
            except BreakException:
                break
            except ContinueException:
                continue

    def visit_class_statement(self, stmt):
        superclass = None

        self.environment.define(stmt.name.lexeme, None)

        if stmt.superclass:
            if not isinstance(superclass := self.evaluate(stmt.superclass), LoxClass):
                raise RuntimeError(stmt.superclass.name, 'superclass must be a class')

            self.environment = Environment(self.environment)
            self.environment.define('super', superclass)

        methods = {}

        for method in stmt.methods:
            methods[method.name.lexeme] = LoxFunction(
                method,
                self.environment,
                method.name.lexeme == 'init'
            )

        if stmt.superclass:
            self.environment = self.environment.enclosing

        self.environment.assign(stmt.name, LoxClass(stmt.name.lexeme, methods, superclass))
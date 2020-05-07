# coding: utf-8

__all__ = ('Statement', 'VarStatement', 'PrintStatement', 'ExpressionStatement')

class Statement:
	pass

class PrintStatement(Statement):
	def __init__(self, expr):
		self.expression = expr

	def accept(self, visitor):
		visitor.visit_print_statement(self)

class ExpressionStatement(Statement):
	def __init__(self, expr):
		self.expression = expr

	def accept(self, visitor):
		visitor.visit_expression_statement(self)

class VarStatement(Statement):
	def __init__(self, name, expr):
		self.name = name
		self.initializer = expr

	def accept(self, visitor):
		pass
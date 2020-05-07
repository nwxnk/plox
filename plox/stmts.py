# coding: utf-8

__all__ = ('Statement', 'PrintStatement', 'ExpressionStatement')

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
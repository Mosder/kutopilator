import AST
import SymbolTable
from Memory import *
from Exceptions import  *
from visit import *
import sys

sys.setrecursionlimit(10000)

class Operations:
    def __init__(self):
        self.op_str_to_fun = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y,
            '.+': lambda x, y: self.mat_vec_op(x, y, '+'),
            '.-': lambda x, y: self.mat_vec_op(x, y, '-'),
            '.*': lambda x, y: self.mat_vec_op(x, y, '*'),
            './': lambda x, y: self.mat_vec_op(x, y, '/'),
            '<': lambda x, y: x < y,
            '>': lambda x, y: x > y,
            '<=': lambda x, y: x <= y,
            '>=': lambda x, y: x >= y,
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y
        }

    def mat_vec_op(self, x, y, op_str):
        op = self.op_str_to_fun.get(op_str)
        for i in range(len(x)):
            if isinstance(x[0], list):
                for j in range(len(x[i])):
                    x[i][j] = op(x[i][j], y[i][j])
            else:
                x[i] = op(x[i], y[i])
        return x

    def from_str(self, op_str, x, y):
        return self.op_str_to_fun.get(op_str)(x, y)

ops = Operations()

class Interpreter(object):
    @on('node')
    def visit(self, node):
        pass

    @when(AST.IntNum)
    def visit(self, node):
        return int(node.value)

    @when(AST.FloatNum)
    def visit(self, node):
        return float(node.value)

    @when(AST.String)
    def visit(self, node):
        return str(node.value)

    @when(AST.Variable)
    def visit(self, node):
        return self.memory.get(node.name)

    @when(AST.BinExpr)
    def visit(self, node):
        r1 = node.left.accept(self)
        r2 = node.right.accept(self)
        return ops.from_str(node.op, r1, r2)

    @when(AST.RelExpr)
    def visit(self, node):
        r1 = node.left.accept(self)
        r2 = node.right.accept(self)
        return ops.from_str(node.op, r1, r2)

    @when(AST.UnaryExpr)
    def visit(self, node):
        pass

    @when(AST.AssignExpr)
    def visit(self, node):
        pass

    @when(AST.Block)
    def visit(self, node):
        pass

    @when(AST.If)
    def visit(self, node):
        pass

    @when(AST.While)
    def visit(self, node):
        r = None
        while node.cond.accept(self):
            r = node.body.accept(self)
        return r

    @when(AST.For)
    def visit(self, node):
        pass

    @when(AST.Break)
    def visit(self, node):
        pass

    @when(AST.Continue)
    def visit(self, node):
        pass

    @when(AST.Return)
    def visit(self, node):
        pass

    @when(AST.Print)
    def visit(self, node):
        pass

    @when(AST.Zeros)
    def visit(self, node):
        pass

    @when(AST.Eye)
    def visit(self, node):
        pass

    @when(AST.Ones)
    def visit(self, node):
        pass

    @when(AST.Transpose)
    def visit(self, node):
        pass

    @when(AST.Reference)
    def visit(self, node):
        pass

    @when(AST.Vector)
    def visit(self, node):
        pass

    @when(AST.Range)
    def visit(self, node):
        pass


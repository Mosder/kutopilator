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
            '!=': lambda x, y: x != y,
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
        r1 = node.variable.accept(self)
        return -r1

    @when(AST.AssignExpr)
    def visit(self, node):
        r1 = node.right.accept(self)
        if isinstance(node.left, AST.Variable):
            r1 = r1 if node.op == '=' else ops.from_str(node.op[0], self.memory.get(node.left.name), r1)
            self.memory.set(node.left.name, r1)
        else: # Reference
            array = self.memory.get(node.left.array.name)
            if len(node.left.indices) == 1: #1D
                r1 = r1 if node.op == '=' else ops.from_str(node.op[0], array[node.left.indices[0].accept(self)], r1)
                array[node.left.indices[0].accept(self)] = r1
                self.memory.set(node.left.array.name, array)
            else: #2D
                r1 = r1 if node.op == '=' else ops.from_str(node.op[0], array[node.left.indices[0].accept(self)][node.left.indices[1].accept(self)], r1)
                array[node.left.indices[0].accept(self)][node.left.indices[1].accept(self)] = r1
                self.memory.set(node.left.array.name, array)

    @when(AST.Block)
    def visit(self, node):
        self.memory = MemoryStack("global")
        for instruction in node.content:
            instruction.accept(self)

    @when(AST.If)
    def visit(self, node):
        instruction = None
        if node.condition.accept(self):
            instruction = node.instruction
        elif node.else_instruction:
            instruction = node.else_instruction

        if instruction:
            self.memory.push("if")
            try:
                if isinstance(instruction, AST.Block):
                    for inst in instruction.content:
                        inst.accept(self)
                else:
                    instruction.accept(self)
            except ContinueException as e:
                raise e
            except BreakException as e:
                raise e
            except ReturnValueException as e:
                raise e
            finally:
                self.memory.pop()

    @when(AST.While)
    def visit(self, node):
        self.memory.push("while")
        while node.condition.accept(self):
            try:
                if isinstance(node.instruction, AST.Block):
                    for inst in node.instruction.content:
                        inst.accept(self)
                else:
                    node.instruction.accept(self)
            except ContinueException:
                continue
            except BreakException:
                break
        self.memory.pop()

    @when(AST.For)
    def visit(self, node):
        start = node.Range.left.accept(self)
        end = node.Range.right.accept(self)
        var_name = node.variable.name
        self.memory.push("for")
        self.memory.set(var_name, start)
        while self.memory.get(var_name) <= end:
            try:
                if isinstance(node.instruction, AST.Block):
                    for inst in node.instruction.content:
                        inst.accept(self)
                else:
                    node.instruction.accept(self)
            except ContinueException:
                continue
            except BreakException:
                break
            finally:
                self.memory.set(var_name, self.memory.get(var_name) + 1)
        self.memory.pop()

    @when(AST.Break)
    def visit(self, node):
        raise BreakException()

    @when(AST.Continue)
    def visit(self, node):
        raise ContinueException()

    @when(AST.Return)
    def visit(self, node):
        raise ReturnValueException(node.value.accept(self))

    @when(AST.Print)
    def visit(self, node):
        for val in node.values:
            print(val.accept(self), end=' ')
        print()

    @when(AST.Zeros)
    def visit(self, node):
        if len(node.values) == 1:
            return [[0 for _ in range(node.values[0].accept(self))] for _ in range(node.values[0].accept(self))]
        else:
            return [[0 for _ in range(node.values[1].accept(self))] for _ in range(node.values[0].accept(self))]

    @when(AST.Eye)
    def visit(self, node):
        return [[1 if i == j else 0 for i in range(node.value.accept(self))] for j in range(node.value.accept(self))]

    @when(AST.Ones)
    def visit(self, node):
        if len(node.values) == 1:
            return [[1 for _ in range(node.values[0].accept(self))] for _ in range(node.values[0].accept(self))]
        else:
            return [[1 for _ in range(node.values[1].accept(self))] for _ in range(node.values[0].accept(self))]

    @when(AST.Transpose)
    def visit(self, node):
        mat = node.value.accept(self)
        if isinstance(mat[0], list):
            return [[x[j][i] for j in range(len(mat))] for i in range(len(mat[0]))]
        else:
            return mat

    @when(AST.Reference)
    def visit(self, node):
        arr = self.memory.get(node.array.name)
        if len(node.indices) == 1: #1D
            return arr[node.indices[0].accept(self)]
        else: #2D
            return arr[node.indices[0].accept(self)][node.indices[1].accept(self)]

    @when(AST.Vector)
    def visit(self, node):
        return [x.accept(self) for x in node.elements]

    @when(AST.Range)
    def visit(self, node):
        return [i for i in range(node.left.accept(self), node.right.accept(self)+1)]


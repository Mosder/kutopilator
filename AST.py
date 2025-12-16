class Node(object):
    pass

class IntNum(Node):
    def __init__(self, value, lineno):
        self.value = value
        self.lineno = lineno

class FloatNum(Node):
    def __init__(self, value, lineno):
        self.value = value
        self.lineno = lineno

class String(Node):
    def __init__(self, value, lineno):
        self.value = value
        self.lineno = lineno

class Variable(Node):
    def __init__(self, name, lineno):
        self.name = name
        self.lineno = lineno

class BinExpr(Node):
    def __init__(self, op, left, right, lineno):
        self.op = op
        self.left = left
        self.right = right
        self.lineno = lineno

class RelExpr(Node):
    def __init__(self, op, left, right, lineno):
        self.op = op
        self.left = left
        self.right = right
        self.lineno = lineno

class UnaryExpr(Node):
    def __init__(self, op, variable, lineno):
        self.op = op
        self.variable = variable
        self.lineno = lineno

class AssignExpr(Node):
    def __init__(self, op, left, right, lineno):
        self.op = op
        self.left = left
        self.right = right
        self.lineno = lineno

class Block(Node):
    def __init__(self, content, lineno):
        self.content = content
        self.lineno = lineno

class If(Node):
    def __init__(self, condition, instruction, lineno, else_instruction=None):
        self.condition = condition
        self.instruction = instruction
        self.else_instruction = else_instruction
        self.lineno = lineno

class While(Node):
    def __init__(self, condition, instruction, lineno):
        self.condition = condition
        self.instruction = instruction
        self.lineno = lineno

class For(Node):
    def __init__(self, variable, Range, instruction, lineno):
        self.variable = variable
        self.Range = Range
        self.instruction = instruction
        self.lineno = lineno

class Break(Node):
    def __init__(self, lineno):
        self.lineno = lineno

class Continue(Node):
    def __init__(self, lineno):
        self.lineno = lineno

class Return(Node):
    def __init__(self, value, lineno):
        self.value = value
        self.lineno = lineno

class Print(Node):
    def __init__(self, values, lineno):
        self.values = values
        self.lineno = lineno

class Zeros(Node):
    def __init__(self, values, lineno):
        self.values = values
        self.lineno = lineno

class Eye(Node):
    def __init__(self, value, lineno):
        self.value = value
        self.lineno = lineno

class Ones(Node):
    def __init__(self, values, lineno):
        self.values = values
        self.lineno = lineno

class Transpose(Node):
    def __init__(self, value, lineno):
        self.value = value
        self.lineno = lineno

class Reference(Node):
    def __init__(self, array, indices, lineno):
        self.array = array
        self.indices = indices
        self.lineno = lineno

class Vector(Node):
    def __init__(self, elements, lineno):
        self.elements = elements
        self.lineno = lineno

class Range(Node):
    def __init__(self, left, right, lineno):
        self.left = left
        self.right = right
        self.lineno = lineno

class Error(Node):
    def __init__(self, lineno):
        self.lineno = lineno

    

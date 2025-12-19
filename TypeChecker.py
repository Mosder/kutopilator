#!/usr/bin/python
from SymbolTable import Symbol, SymbolTable
import AST

class Type:
    def __init__(self, obj_type, shape, error = None, line = None):
        self.obj_type = obj_type
        self.shape = shape
        self.error = error
        self.line = line

class NodeVisitor(object):
    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):        # Called if no explicit visitor function exists for a node.
        if isinstance(node, list):
            for elem in node:
                self.visit(elem)
        else:
            for child in node.children:
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, AST.Node):
                            self.visit(item)
                elif isinstance(child, AST.Node):
                    self.visit(child)

    # simpler version of generic_visit, not so general
    #def generic_visit(self, node):
    #    for child in node.children:
    #        self.visit(child)



class TypeChecker(NodeVisitor):
    def __init__(self):
        self.symtab = SymbolTable()
        self.loop_depth = 0

    def error(self, node, msg):
        print(f"[{node.lineno}]: {msg}")
        return Type("error", None, error=msg, line=node.lineno)

    def coerce_types(self, T1, T2, origin):
        shape = None
        if self.is_scalar(T1) and self.is_scalar(T2):
            shape = 0
        if self.is_vector(T1) and self.is_vector(T2):
            if T1.shape == T2.shape:
                shape = T1.shape
            if T1.shape == -1 or T2.shape == -1:
                shape = -1
        if self.is_matrix(T1) and self.is_matrix(T2):
            if T1.shape == T2.shape:
                shape = T1.shape
            if T1.shape[0] == T2.shape[0]:
                if T1.shape[1] == -1 or T2.shape[1] == -1:
                    shape = (T1.shape[0], -1)
            if T1.shape[1] == T2.shape[1]:
                if T1.shape[0] == -1 or T2.shape[0] == -1:
                    shape = (-1, T1.shape[1])

        if shape is None:
            return self.error(origin, f"Incompatible shapes: {T1.shape}, {T2.shape}")
            
        if T1.obj_type == 'float' or T2.obj_type == 'float':
            return Type('float', shape)
        if T1.obj_type == 'int' and T2.obj_type == 'int':
            return Type('int', shape)
        if T1.obj_type == 'string' and T2.obj_type == 'int':
            return Type('string', 0)
        if T1.obj_type == 'int' and T2.obj_type == 'string':
            return Type('string', 0)
        return self.error(origin, f"Couldn't coerce types {T1.obj_type}, {T2.obj_type}")

    def is_scalar(self, T):
        return T.shape == 0

    def is_vector(self, T):
        return isinstance(T.shape, int) and T.shape != 0

    def is_matrix(self, T):
        return isinstance(T.shape, tuple)

    def visit_IntNum(self, node):
        return Type('int', 0)

    def visit_FloatNum(self, node):
        return Type('float', 0)

    def visit_String(self, node):
        return Type('string', 0)

    def visit_Variable(self, node):
        entry = self.symtab.get(node.name)
        if entry is None:
            return Type('undefined', None)
        return entry.type

    def visit_BinExpr(self, node):
        left = self.visit(node.left)     # type1 = node.left.accept(self) 
        right = self.visit(node.right)    # type2 = node.right.accept(self)
        op = node.op
        
        if op in ['+', '-', '*', '/']:
            if self.is_scalar(left) and self.is_scalar(right):
                return self.coerce_types(left, right, node)
            return self.error(node, f"{op} is unsupported for non-scalar types")

        if op in ['.+', '.-', '.*', './']:
            if (self.is_vector(left) and self.is_vector(right)) or (self.is_matrix(left) and self.is_matrix(right)):
                return self.coerce_types(left, right, node)
            return self.error(node, f"Incompatible shapes: {left.shape}, {right.shape} for operation: {op}")
                            
        return self.error(node, f"Unknown operation: {op}")

    def visit_RelExpr(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op

        if op in ['<', '>', '<=', '>=']:
            if left.obj_type == right.obj_type:
                if self.is_scalar(left) and self.is_scalar(right):
                    return Type('bool', 0)
                return self.error(node, f"Comparison of non-scalar values not allowed")
            return self.error(node, f"Incompatible types for comparison: {left.obj_type}, {right.obj_type}")

        if op in ['!=', '==']:
            return Type('bool', 0)
        
        return self.error(node, f"Unknown operation: {op}")

    def visit_UnaryExpr(self, node):
        variable = self.visit(node.variable)
        op = node.op

        if op == '-':
            if self.is_scalar(variable):
                if variable.obj_type == 'float' or variable.obj_type == 'int':
                    return variable
                return self.error(node, f"Incompatible type: {variable.obj_type} for operation {op}")
            return self.error(node, f"{op} is unsupported for non-scalar types")
        return self.error(node, f"Unknown operation: {op}")

    def visit_AssignExpr(self, node):
        left_t = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op

        if isinstance(node.left, AST.Variable):
            self.symtab.put(node.left.name, Symbol(node.left.name, right))
            return Type('void', None)

        if isinstance(node.left, AST.Reference):
            if left_t.obj_type == right.obj_type:
                if left_t.shape == right.shape:
                    return Type('void', None)
                return self.error(node, f"Incompatible shapes: {left_t.shape}, {right.shape}")
            return self.error(node, f"Incompatible types: {left_t.obj_type}, {right.obj_type}")

        return self.error(node, f"Unassignable type: {left_t.obj_type}")
                                    
    def visit_Block(self, node):
        old = self.symtab
        self.symtab = self.symtab.pushScope("block")

        for stmt in node.content:
            self.visit(stmt)

        self.symtab = self.symtab.popScope()
        return Type('void', None)

    def visit_If(self, node):
        condition = self.visit(node.condition)
        if condition.obj_type != "bool":
            return self.error(node, f"If condition must be boolean found {condition.obj_type}")

        self.visit(node.instruction)
        if node.else_instruction is not None:
            self.visit(node.else_instruction)
            
        return Type('void', None)

    def visit_While(self, node):
        condition = self.visit(node.condition)
        if condition.obj_type != "bool":
            return self.error(node, f"While condition must be boolean found {condition.obj_type}")

        self.loop_depth += 1
        self.visit(node.instruction)
        self.loop_depth -= 1
            
        return Type('void', None)

    def visit_For(self, node):
        range_t = self.visit(node.Range)

        if not self.is_vector(range_t):
            return self.error(node, f"Incompatible shape of range expression: {range_t.shape}")

        variable_t = Type(range_t.obj_type, 0)

        self.symtab.put(node.variable.name, Symbol(node.variable.name, variable_t))

        self.loop_depth += 1
        self.visit(node.instruction)
        self.loop_depth -= 1

        return Type('void', None)
    
    def visit_Break(self, node):
        if self.loop_depth == 0:
            return self.error(node, "'break' used outside of loop")
        return Type("void", 0)
        
    def visit_Continue(self, node):
        if self.loop_depth == 0:
            return self.error(node, "'continue' used outside of loop")
        return Type("void", 0)

    def visit_Return(self, node):
        value = self.visit(node.value)

        if value.obj_type == 'void':
            return self.error(node, f"Invalid return type: {value.obj_type}")

        return value

    def visit_Print(self, node):
        for v in node.values:
            value = self.visit(v)
            if value.obj_type not in ['string', 'int', 'float', 'bool']:
                return self.error(node, f"Invalid print argument type: {value.obj_type}")
        
        return Type("void", 0)

    def visit_Zeros(self, node):
        args = len(node.values)
        if args < 1 or args > 2:
            return self.error(node, f"Expected 1 or 2 arguments, received: {args}")
        
        for v in node.values:
            value = self.visit(v)
            if not self.is_scalar(value):
                return self.error(node, "zeros() only supports scalar values")
            if value.obj_type != 'int':
                return self.error(node, f"Invalid zeros argument type: {value.obj_type}")

            if isinstance(v, AST.IntNum):
                if v.value < 1:
                    return self.error(node.value, f"Only positive arguments allowed, received: {v.value}")

        if args == 1 and isinstance(node.values[0], AST.IntNum):
            return Type('int', (node.values[0].value, node.values[0].value))

        if args == 2 and isinstance(node.values[0], AST.IntNum) and isinstance(node.values[1], AST.IntNum):
            return Type('int', (node.values[0].value, node.values[1].value))

        return Type('int', (-1, -1))

    def visit_Eye(self, node):
        value = self.visit(node.value)

        if not self.is_scalar(value):
            return self.error(node, "eye() only supports scalar values")
        if value.obj_type != 'int':
            return self.error(node, f"Invalid eye argument type: {value.obj_type}")

        if isinstance(node.value, AST.IntNum):
            shape = node.value.value
            if shape < 1:
                return self.error(node.value, "Only positive arguments allowed")
            return Type('int', (shape, shape))

        return Type('int', (-1, -1))

    def visit_Ones(self, node):
        args = len(node.values)
        if args < 1 or args > 2:
            return self.error(node, f"Expected 1 or 2 arguments, received: {args}")
        
        for v in node.values:
            value = self.visit(v)
            if not self.is_scalar(value):
                return self.error(node, "ones() only supports scalar values")
            if value.obj_type != 'int':
                return self.error(node, f"Invalid ones argument type: {value.obj_type}")

            if isinstance(v, AST.IntNum):
                if v.value < 1:
                    return self.error(node.value, f"Only positive arguments allowed, received: {v.value}")
                
        if args == 1 and isinstance(node.values[0], AST.IntNum):
            return Type('int', (node.values[0].value, node.values[0].value))

        if args == 2 and isinstance(node.values[0], AST.IntNum) and isinstance(node.values[1], AST.IntNum):
            return Type('int', (node.values[0].value, node.values[1].value))

        return Type('int', (-1, -1))

    def visit_Transpose(self, node):
        value = self.visit(node.value)

        if self.is_vector(value):
            return value
        
        if self.is_matrix(value):
            return Type(value.obj_type, (value.shape[1], value.shape[0]))

        return self.error(node, f"Incompatible shape: {value.shape}")

    def visit_Reference(self, node):
        array = self.visit(node.array)
        indices = len(node.indices)
        
        if indices < 1:
            return self.error(node, "Index list empty")
        
        if self.is_vector(array):
            for i in node.indices:
                i_type = self.visit(i)
                if not self.is_scalar(i_type) or i_type.obj_type != 'int':
                    return self.error(i, f"Can only reference integer scalars")
                if isinstance(i, AST.IntNum):
                    if i.value < 0 or i.value > array.shape:
                        return self.error(i, f"Index {i.value} out of bound for array of size {array.shape}")
            return Type(array.obj_type, indices)

        if self.is_matrix(array):
            indices = len(node.indices)
            if indices > 2:
                return self.error(node, f"Matrices are indexed using 2 value tuples, got {indices}")
            current_i = 0
            for i in node.indices:
                i_type = self.visit(i)
                if not self.is_scalar(i_type) or i_type.obj_type != 'int':
                    return self.error(i, f"Can only reference integer scalars")
                if isinstance(i, AST.IntNum):
                    if i.value < 0 or i.value > array.shape[current_i]:
                        return self.error(i, f"Index {i.value} out of bound for Matrix of column/row size {array.shape[current_i]}")
                current_i += 1
            return Type(array.obj_type, 0)

        return self.error(node, f"Cannot reference object of type {array.obj_type}")

    def visit_Vector(self, node):
        elements = []
        for e in node.elements:
            elements.append(self.visit(e))
            
        first = elements[0]
        
        for t in elements:
            if t.shape != first.shape:
                return self.error(node, f"Incompatible shapes: {t.shape}, {first.shape}")
            if t.obj_type != first.obj_type:
                return self.error(node, f"Incompatible types: {t.obj_type}, {first.obj_type}")

        if self.is_scalar(first):
            return Type(first.obj_type, len(elements))

        if self.is_vector(first):
            return Type(first.obj_type, (len(elements), first.shape))

        return self.error(node, "Cannot create arbitrary tensor")
            
    def visit_Range(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        for t in (left, right):
            if t.obj_type != "int" or not self.is_scalar(t):
                return self.error(node, f"Range bounds must be integer scalars")

        shape = -1
        if isinstance(node.left, AST.IntNum) and isinstance(node.right, AST.IntNum):
            shape = abs(node.right.value - node.left.value)
        
        return Type("int", shape)

        

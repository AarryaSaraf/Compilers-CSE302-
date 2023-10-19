from .bxast import *
from typing import Set
from .bxtypes import *

class TypeCheckFail:
    def __init__(self, expr, ty: Type, expected_ty: Type):
        self.expr = expr
        self.ty = ty
        self.expected_ty = expected_ty

    def print(self):
        print(
            f"expected type {self.expected_ty} of expression {self.expr} but got {self.ty}"
        )


@dataclass
class SyntaxError:
    msg: str

class SyntaxChecker:
    def __init__(self) -> None:
        self.errors = []

    def check_program(self, program: List[Function | StatementDecl]):
        for glob in program:
            match glob:
                case Function():
                    self.check_function(glob)
                case StatementDecl(name, ty, init) if not isinstance(init, (ExpressionInt, ExpressionBool)):
                    self.errors.append(SyntaxError(f"Global variable {name} can only take static expressions as input"))
        return self.errors
                
    def check_function(self, fun: Function) -> List[SyntaxError]:
        if fun.name != "main":
            self.errors.append(
                SyntaxError(f"expected function name to be 'main' but got: {fun.name}")
            )
        vardecl = set()
        for stmt in fun.body.stmts:
            self.check_stmt(stmt, vardecl)


    def check_stmt(self, stmt: Statement, vardecl: Set[str]) -> List[SyntaxError]:
        match stmt:
            case StatementAssign(lvalue, rvalue):
                if lvalue not in vardecl:
                    self.errors.append(
                        SyntaxError(
                            f"Variable {lvalue} undefined, must declare before write"
                        )
                    )
                self.check_expr(rvalue, vardecl)
            case StatementDecl(name, _, expr):
                self.check_expr(expr, vardecl)
                vardecl.add(name)
            case StatementEval(expr):
                self.check_expr(expr, vardecl)


    def check_expr(self, expr: Expression, vardecl: Set[str]) -> List[SyntaxError]:
        match expr:
            case ExpressionVar(name):
                if name not in vardecl:
                    self.errors.append(
                        SyntaxError(f"Variable {name} undefined, must declare before read")
                    )
                return []
            case ExpressionInt(n):
                if n < 0 or n > 2**63:
                    self.errors.append(SyntaxError(f"Integer value {n} is out of bounds"))
                return []
            case ExpressionBinOp(_, left, right):
                return self.check_expr(left, vardecl) + self.check_expr(right, vardecl)
            case ExpressionCall(target, args):
                if target != "print":
                    self.errors.append(
                        [
                            SyntaxError(
                                f"We currently don't support any call to {target}, only 'print' is allowed"
                            )
                        ]
                    )
                for arg in args:
                    self.check_expr(arg, vardecl)
            case ExpressionUniOp(_, arg):
                return self.check_expr(arg, vardecl)
            case _:
                return []


    def pp_errs(errors: List[SyntaxError]):
        for err in errors:
            print(f"\x1b[31mError:\x1b[0m {err.msg}")


class TypeChecker:
    def __init__(self) -> None:
        self.var_scope_stack = []
        self.function_signatures = {}
        self.errors = []
        self.expected_return = None

    def identify_global_scope(self, program: List[StatementDecl | Function]):
       global_vars = {var.name: var.ty for var in program if isinstance(var, StatementDecl) }
       self.var_scope_stack = [global_vars]
       self.function_signatures = {fun.name: fun.ty for fun in program if isinstance(fun, Function)}

    def infer_type(self, expr: Expression):
        match expr:
            case ExpressionInt(): return PrimiType("int")
            case ExpressionBool(): return PrimiType("bool")
            case ExpressionVar(name):
                return self.lookup_type(name)
            case ExpressionCall(target, args):
                if target == "print":
                    return VoidType()
                fty = self.function_signatures[target].ty
                for exp_ty, arg in zip(fty.input_types, args):
                    self.assert_type(exp_ty, arg)
                return PrimiType(fty.out_type)
            case ExpressionBinOp(op, left, right):
                if op.startswith("boolean"):
                    self.assert_type(PrimiType("bool"), left)
                    self.assert_type(PrimiType("bool"), right)
                    return PrimiType("bool")
                if op in ["lt", "lte", "gt", "gte", "equals", "notequals"]:
                    self.assert_type(PrimiType("int"), left)
                    self.assert_type(PrimiType("int"), right)
                    return PrimiType("bool")
                else:
                    self.assert_type(PrimiType("int"), left)
                    self.assert_type(PrimiType("int"), right)

                    return PrimiType("int")
            case ExpressionUniOp(op, arg):
                if op == "boolean-negation":
                    self.assert_type(PrimiType("bool"), arg)
                    return PrimiType("bool")
                else:
                    self.assert_type(PrimiType("int"), arg)
                    return PrimiType("int")
    
    def assert_type(self, expected: Type, expr: Expression):
        got = self.infer_type(expr)
        if got != expected:
            self.errors.append(TypeCheckFail(expr, got, expected))

    def lookup_type(self, varname: str):
         for scope in reversed(self.var_scope_stack):
            if varname in scope:
                return scope[varname]
            
    def check_stmt(self, stmt: Statement):
        match stmt:
            case StatementDecl(name, ty, init):
                self.assert_type(ty, init)
                self.var_scope_stack[-1][name] = ty
            case StatementAssign(lvalue, rvalue):
                self.assert_type(self.lookup_type(lvalue), rvalue)
            case StatementBlock(block):
                self.check_block(block)
            case StatementEval(expr):
                self.infer_type(expr) # will do the checking for all subexpressions
            case StatementIf(cond, body, elseblock):
                self.assert_type(PrimiType("bool"), cond)
                self.check_block(body)
                if elseblock is not None:
                    self.check_block(elseblock)
            case StatementWhile(cond, body):
                self.assert_type(PrimiType("bool"), cond)
                self.check_block(body)
            case StatementReturn(expr):
                if expr is not None:
                    self.assert_type(self.expected_return, expr)
                elif not isinstance(self.expected_return, VoidType):
                    self.errors.append(self.expected_return, VoidType, expr)
    def check_block(self, block: Block):
        self.var_scope_stack.append({})
        for stmt in block.stmts:
            self.check_stmt(stmt)
        self.var_scope_stack = self.var_scope_stack[:-1]
    
    def check_function(self, fun: Function):
        self.var_scope_stack.append({p[0]: p[1] for p in fun.params})
        self.expected_return = fun.return_ty
        self.check_block(fun.body)
    
    def check(self, program: List[Function | StatementDecl]) -> List[TypeCheckFail]:
        self.identify_global_scope(program)
        for fun in program:
            if isinstance(fun, Function):
                self.check_function(fun)
        for err in self.errors:
            err.print()
        return self.errors
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
        self.scope_stack: List[Set] = []
        self.loop_depth = 0
        self.functions = {}
        self.set_runtime_functions()

    def set_runtime_functions(self):
        self.functions["print"] = Function(
            "print", None, VoidType, [("x", PrimiType("any"))]
        )
        self.functions["readint"] = Function("readint", None, PrimiType("int"), [])

    def check_program(self, program: List[Function | StatementDecl]):
        self.scope_stack = [
            set([decl.name for decl in program if isinstance(decl, StatementDecl)])
        ]
        self.functions = self.functions | {
            fun.name: fun for fun in program if isinstance(fun, Function)
        }

        for glob in program:
            match glob:
                case Function():
                    self.check_function(glob)
                case StatementDecl(name, ty, init) if not isinstance(
                    init, (ExpressionInt, ExpressionBool)
                ):
                    self.errors.append(
                        SyntaxError(
                            f"Global variable {name} can only take static expressions as input"
                        )
                    )
        if not any(
            [fun.name == "main" for fun in program if isinstance(fun, Function)]
        ):
            self.errors.append(SyntaxError("Expected a main function"))
        return self.errors

    def check_function(self, fun: Function) -> List[SyntaxError]:
        self.scope_stack.append(set([p[0] for p in fun.params]))
        for stmt in fun.body.stmts:
            self.check_stmt(stmt)
        self.scope_stack.pop(-1)

    def defined(self, varname: str):
        for scope in reversed(self.scope_stack):
            if varname in scope:
                return True
        return False

    def check_stmt(self, stmt: Statement) -> List[SyntaxError]:
        match stmt:
            case StatementAssign(lvalue, rvalue):
                if not self.defined(lvalue):
                    self.errors.append(
                        SyntaxError(
                            f"Variable {lvalue} undefined, must declare before write"
                        )
                    )
                self.check_expr(rvalue)
            case StatementDecl(name, _, expr):
                self.check_expr(expr)
                self.scope_stack[-1].add(name)
            case StatementEval(expr):
                self.check_expr(expr)
            case StatementBlock(block):
                self.scope_stack.append(set())
                for stmt in block.stmts:
                    self.check_stmt(stmt)
                self.scope_stack.pop(-1)
            case StatementBreak():
                if self.loop_depth == 0:
                    self.errors.append(
                        SyntaxError("Cannot use break statement outside of loop")
                    )
            case StatementContinue():
                if self.loop_depth == 0:
                    self.errors.append(
                        SyntaxError("Cannot use continue statement outside of loop")
                    )
            case StatementReturn(expr):
                if expr is not None:
                    self.check_expr(expr)
            case StatementWhile(cond, body):
                self.check_expr(cond)
                self.loop_depth += 1
                self.scope_stack.append(set())
                for stmt in body.stmts:
                    self.check_stmt(stmt)
                self.scope_stack.pop(-1)
                self.loop_depth -= 1
            case StatementIf(cond, body, elseblock):
                self.check_expr(cond)
                self.scope_stack.append(set())
                for stmt in body.stmts:
                    self.check_stmt(stmt)
                self.scope_stack.pop(-1)
                if elseblock is not None:
                    self.scope_stack.append(set())
                    for stmt in body.stmts:
                        self.check_stmt(stmt)
                    self.scope_stack.pop(-1)

    def check_expr(self, expr: Expression):
        match expr:
            case ExpressionVar(name):
                if not self.defined(name):
                    self.errors.append(
                        SyntaxError(
                            f"Variable {name} undefined, must declare before read"
                        )
                    )
            case ExpressionInt(n):
                if n < 0 or n > 2**63:
                    self.errors.append(
                        SyntaxError(f"Integer value {n} is out of bounds")
                    )
            case ExpressionBinOp(_, left, right):
                self.check_expr(left)
                self.check_expr(right)
            case ExpressionCall(target, args):
                if target not in self.functions:
                    self.errors.append(SyntaxError(f"Function {target} is not defined"))
                elif len(args) != len(self.functions[target].params):
                    self.errors.append(
                        SyntaxError(
                            f"Function {target} takes {len(self.functions[target].params)} arguments but {len(args)} where given"
                        )
                    )
                for arg in args:
                    self.check_expr(arg)
            case ExpressionUniOp(_, arg):
                self.check_expr(arg)

    def pp_errs(self, errors: List[SyntaxError]):
        for err in errors:
            print(f"\x1b[31mError:\x1b[0m {err.msg}")


class TypeChecker:
    def __init__(self) -> None:
        self.var_scope_stack = []
        self.function_signatures = {}
        self.errors = []
        self.expected_return = None

    def identify_global_scope(self, program: List[StatementDecl | Function]):
        global_vars = {
            var.name: var.ty for var in program if isinstance(var, StatementDecl)
        }
        self.var_scope_stack = [global_vars]
        self.function_signatures = {
            fun.name: fun.ty for fun in program if isinstance(fun, Function)
        }
        self.set_runtime_functions()

    def set_runtime_functions(self):
        self.function_signatures["readint"] = FunctionType(
            input_types=[], out_type=PrimiType("int")
        )

    def infer_type(self, expr: Expression):
        match expr:
            case ExpressionInt():
                expr.ty = PrimiType("int")
            case ExpressionBool():
                expr.ty = PrimiType("bool")
            case ExpressionVar(name):
                expr.ty = self.lookup_type(name)
            case ExpressionCall(target, args):
                if target == "print":
                    expr.ty = VoidType()
                    argty = self.infer_type(args[0])
                    if argty == PrimiType("int"):
                        expr.target = "__bx_print_int"
                    if argty == PrimiType("bool"):
                        expr.target = "__bx_print_bool"
                else:
                    fty = self.function_signatures[target]
                    for exp_ty, arg in zip(fty.input_type, args):
                        self.assert_type(exp_ty, arg)
                    expr.ty = fty.out_type
            case ExpressionBinOp(op, left, right):
                if op.startswith("boolean"):
                    self.assert_type(PrimiType("bool"), left)
                    self.assert_type(PrimiType("bool"), right)
                    expr.ty = PrimiType("bool")
                elif op in ["lt", "lte", "gt", "gte", "equals", "notequals"]:
                    self.assert_type(PrimiType("int"), left)
                    self.assert_type(PrimiType("int"), right)
                    expr.ty = PrimiType("bool")
                else:
                    self.assert_type(PrimiType("int"), left)
                    self.assert_type(PrimiType("int"), right)
                    expr.ty = PrimiType("int")
            case ExpressionUniOp(op, arg):
                if op == "boolean-negation":
                    self.assert_type(PrimiType("bool"), arg)
                    expr.ty = PrimiType("bool")
                else:
                    self.assert_type(PrimiType("int"), arg)
                    expr.ty = PrimiType("int")
        return expr.ty

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
                self.infer_type(expr)  # will do the checking for all subexpressions
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

from .bxast import *
from typing import Set

@dataclass
class SyntaxError:
    msg: str

def check_programm(program: Function)->List[SyntaxError]:
    errors = []
    if program.name != "main":
        errors.append(SyntaxError(f"expected function name to be 'main' but got: {program.name}"))
    vardecl = set()
    for stmt in program.stmts:
        errors += check_stmt(stmt, vardecl)
    return errors

def check_stmt(stmt: Statement, vardecl: Set[str]) -> List[SyntaxError]:
    errors = []
    match stmt:
        case StatementAssign(lvalue, rvalue):
            if lvalue not in vardecl:
                errors.append(SyntaxError(f"Variable {lvalue} undefined, must declare before write"))
            errors += check_expr(rvalue, vardecl)
        case StatementDecl(name, _, expr):
            errors += check_expr(expr, vardecl)
            vardecl.add(name)
        case StatementEval(expr):
            errors += check_expr(expr, vardecl)
    return errors

def check_expr(expr: Expression, vardecl: Set[str]) -> List[SyntaxError]:
    match expr:
        case ExpressionVar(name):
            if name not in vardecl:
                return [SyntaxError(f"Variable {name} undefined, must declare before read")]
            return []
        case ExpressionInt(n):
            if n < 0 or n > 2**63:
                return [SyntaxError(f"Integer value {n} is out of bounds")]
            return []
        case ExpressionBinOp(_, left, right):
            return check_expr(left, vardecl)+check_expr(right, vardecl)
        case ExpressionCall(target, args):
            errors = []
            if target != "print":
                errors.append([SyntaxError(f"We currently don't support any call to {target}, only 'print' is allowed")])
            for arg in args:
                errors += check_expr(arg, vardecl)
            return errors
        case ExpressionUniOp(_, arg):
            return check_expr(arg, vardecl)
        case _:
            return []

def pp_errs(errors: List[SyntaxError]):
    for err in errors:
        print(f"\x1b[31mError:\x1b[0m {err.msg}")
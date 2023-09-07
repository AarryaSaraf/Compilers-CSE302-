from .ast import *
from .tac import *

def tmm(statments, var_to_tmp):
    code = []
    for stmt in statments:
        match stmt: 
            case StatementAssign(var, expr): code += tmm_code(expr, var_to_tmp[var], var_to_tmp)
            case StatementEval(expr): code += tmm_code(expr, None, var_to_tmp)
            case StatementDecl(name): code += [TACOp("const", [0], var_to_tmp[name])]
    return code

def tmm_code(expr, result, var_to_tmp) -> List[TACOp]:
    match expr:
        case ExpressionVar(name): 
            return [TACOp("copy", [var_to_tmp[name]], result)]
        case ExpressionInt(val):
            return [TACOp("const", [val], result)]
        case ExpressionBinOp(operator, left, right):
            left_tmp = fresh_temp()
            right_tmp = fresh_temp()
            left_ops = tmm_code(left, left_tmp, var_to_tmp)
            right_ops = tmm_code(right, right_tmp, var_to_tmp)
            return left_ops + right_ops + [TACOp(operator, [left_tmp, right_tmp], result)]
        case ExpressionUniOp(operator, arg):
            tmp = fresh_temp()
            arg_op = tmm_code(arg, tmp, var_to_tmp)
            return arg_op + [TACOp(operator, [tmp], result)]
        case ExpressionCall("print", [arg]):
            tmp = fresh_temp()
            arg_op = tmm_code(arg, tmp, var_to_tmp)
            return arg_op + [TACOp("print", [tmp], None)]
        case x:
            raise ValueError(f"cant translate {x}")
        
from .bxast import *
from .tac import *
from typing import Dict, List

def tmm(statments: List[Statement], var_to_tmp: Dict[str, TACTemp]) -> List[TACOp]:
    code = []
    for stmt in statments:
        match stmt: 
            case StatementAssign(var, expr): code += tmm_code(expr, var_to_tmp[var], var_to_tmp)
            case StatementEval(expr): code += tmm_code(expr, None, var_to_tmp)
            case StatementDecl(name): code += [TACOp("const", [0], var_to_tmp[name])]
    return code

def tmm_code(expr: Expression, result: TACTemp, var_to_tmp:  Dict[str, TACTemp]) -> List[TACOp]:
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
            return left_ops + right_ops + [TACOp(OPERATOR_TO_OPCODE[operator], [left_tmp, right_tmp], result)]
        case ExpressionUniOp(operator, arg):
            tmp = fresh_temp()
            arg_op = tmm_code(arg, tmp, var_to_tmp)
            return arg_op + [TACOp(OPERATOR_TO_OPCODE[operator], [tmp], result)]
        case ExpressionCall("print", [arg]):
            tmp = fresh_temp()
            arg_op = tmm_code(arg, tmp, var_to_tmp)
            return arg_op + [TACOp("print", [tmp], None)]
        case x:
            raise ValueError(f"cant translate {x}")
        
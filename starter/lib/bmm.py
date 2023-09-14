from .ast_def import *
from .tac import *
from typing import Dict, List, Tuple

def bmm(statments: List[Statement], var_to_tmp: Dict[str, TACTemp]) -> List[TACOp]:
    code = []
    for stmt in statments:
        match stmt: 
            case StatementAssign(var, expr): 
                res, expr_code  = bmm_code(expr, var_to_tmp)
                code += expr_code + [TACOp("copy", [res], var_to_tmp[var])]
            case StatementEval(expr): 
                res, expr_code = bmm_code(expr, var_to_tmp)
                code += expr_code
            case StatementDecl(name): 
                code += [TACOp("const", [0], var_to_tmp[name])]
    return code

def bmm_code(expr: Expression, var_to_tmp: Dict[str, TACTemp]) -> Tuple[TACTemp, TACOp]:
    match expr:
        case ExpressionVar(name): 
            return var_to_tmp[name], []
        case ExpressionInt(val):
            result = fresh_temp()
            return result, [TACOp("const", [val], result)]
        case ExpressionBinOp(operator, left, right):
            left_tmp, left_ops = bmm_code(left, var_to_tmp)
            right_tmp, right_ops = bmm_code(right, var_to_tmp)
            result = fresh_temp()
            return result, left_ops + right_ops + [TACOp(OPERATOR_TO_OPCODE[operator], [left_tmp, right_tmp], result)]
        case ExpressionUniOp(operator, arg):
            result = fresh_temp()
            arg_tmp, arg_op = bmm_code(arg, var_to_tmp)
            return result, arg_op + [TACOp(OPERATOR_TO_OPCODE[operator], [arg_tmp], result)]
        case ExpressionCall("print", [arg]):
            arg_tmp, arg_op = bmm_code(arg, var_to_tmp)
            return None, arg_op + [TACOp("print", [arg_tmp], None)]
        case x:
            raise ValueError(f"cant translate {x}")
from .bxast import *
from .tac import *
from typing import Dict, List

def tmm(fn: Function, var_to_tmp: Dict[str, TACTemp]) -> TAC:
    return TAC(tmm_block(fn.body, var_to_tmp))

def tmm_block(block: Block, var_to_tmp: Dict[str, TACTemp]) -> List[TAC]:
    code = []
    for stmt in block.stmts:
        match stmt:
            case StatementAssign(var, expr):
                code += tmm_int_code(expr, var_to_tmp[var], var_to_tmp)
            case StatementEval(expr):
                code += tmm_int_code(expr, None, var_to_tmp)
            case StatementDecl(name, ty, init):
                code += tmm_int_code(init, var_to_tmp[name], var_to_tmp)
            case StatementWhile(cond, block):
                label_head, label_body, label_end = fresh_label(), fresh_label(), fresh_label()
                code += [label_head] + tmm_bool_code(cond, label_body, label_end, var_to_tmp) +[label_body]+ tmm_block(block, var_to_tmp) +[TACOp("jmp", [label_head], None)]+ [label_end]
            case StatementIf(cond, thenblock, elseblock):
                label_true, label_false, label_end = fresh_label(), fresh_label(), fresh_label()
                code += tmm_bool_code(cond, label_true, label_false, var_to_tmp) + [label_true] + tmm_block(thenblock, var_to_tmp) +[TACOp("jmp", [label_end], None),label_false]
                if elseblock is not None:
                    code += tmm_block(elseblock, var_to_tmp) + [label_end]
                else:
                    code += [label_end]
    return code

COMPARISON_TOJMPCODE = { 
    "lt": "jl",
    "lte": "jle",
    "gt": "jnle",
    "gte": "jnl" 
}
def tmm_bool_code(expr:Expression, lab_true: TACLabel, lab_false: TACLabel, var_to_tmp: Dict[str, TACTemp])-> List[TACOp | TACLabel]:
    match expr:
        case ExpressionBinOp("equals" | "notequals" | "lt" | "lte" | "gt" | "gte" as op, left, right, _):
            left_tmp = fresh_temp()
            right_tmp = fresh_temp()
            left_ops = tmm_int_code(left, left_tmp, var_to_tmp)
            right_ops = tmm_int_code(right, right_tmp, var_to_tmp)
            match op:
                case "equals":
                    return (
                        left_ops
                        + right_ops 
                        + [
                            TACOp("sub", [left_tmp, right_tmp], left_tmp),
                            TACOp("jz", [left_tmp, lab_true], None),
                            TACOp("jmp", [lab_false], None)
                        ]
                    )
                case "notequals":
                    return (
                        left_ops
                        + right_ops 
                        + [
                            TACOp("sub", [left_tmp, right_tmp], left_tmp),
                            TACOp("jz", [left_tmp, lab_false], None),
                            TACOp("jmp", [lab_true], None)
                        ]
                    )
                case x:
                    return (
                        left_ops
                        + right_ops 
                        + [
                            TACOp("sub", [left_tmp, right_tmp], left_tmp),
                            TACOp(f"{COMPARISON_TOJMPCODE[x]}", [left_tmp, lab_true], None), 
                            TACOp("jmp", [lab_false], None)
                        ]
                    )
        case ExpressionBinOp("boolean-and", left, right, _):
            iterim_label = fresh_label()
            return (
                tmm_bool_code(left, interim_label, lab_false)
                + [interim_label]
                + tmm_bool_code(right, lab_true, lab_false)
            )
        case ExpressionBinOp("boolean-or", left, right, _):
            iterim_label = fresh_label()
            return (
                tmm_bool_code(left, lab_true, interim_label, var_to_tmp)
                + [interim_label]
                + tmm_bool_code(right, lab_true, lab_false, var_to_tmp)
            )
        case ExpressionUniOp("boolean-negation", arg, _):
            return tmm_bool_code(expr, lab_false, lab_true, var_to_tmp)
        case x:
            print(f"Cannot ast2tac the expression: {x}")
        
def tmm_int_code(
    expr: Expression, result: TACTemp, var_to_tmp: Dict[str, TACTemp]
) -> List[TACOp]:
    match expr:
        case ExpressionVar(name):
            return [TACOp("copy", [var_to_tmp[name]], result)]
        case ExpressionInt(val):
            return [TACOp("const", [val], result)]
        case ExpressionBinOp(operator, left, right):
            left_tmp = fresh_temp()
            right_tmp = fresh_temp()
            left_ops = tmm_int_code(left, left_tmp, var_to_tmp)
            right_ops = tmm_int_code(right, right_tmp, var_to_tmp)
            return (
                left_ops
                + right_ops
                + [TACOp(OPERATOR_TO_OPCODE[operator], [left_tmp, right_tmp], result)]
            )
        case ExpressionUniOp(operator, arg):
            tmp = fresh_temp()
            arg_op = tmm_int_code(arg, tmp, var_to_tmp)
            return arg_op + [TACOp(OPERATOR_TO_OPCODE[operator], [tmp], result)]
        case ExpressionCall("print", [arg]):
            tmp = fresh_temp()
            arg_op = tmm_int_code(arg, tmp, var_to_tmp)
            return arg_op + [TACOp("print", [tmp], None)]
        case x:
            raise ValueError(f"cant translate {x}")

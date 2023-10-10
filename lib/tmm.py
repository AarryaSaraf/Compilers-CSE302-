from .bxast import *
from .tac import *
from typing import Dict, List


class TMM(Lowerer):
    def to_tac(self):
        return TAC(self.tmm_block(self.fn.body))

    def tmm_block(self, block: Block) -> List[TAC]:
        code = []
        for stmt in block.stmts:
            match stmt:
                case StatementAssign(var, expr):
                    code += self.tmm_int_code(expr, self.var_to_tmp[var])
                case StatementEval(expr):
                    code += self.tmm_int_code(expr, None)
                case StatementDecl(name, ty, init):
                    code += self.tmm_int_code(init, self.var_to_tmp[name])
                case StatementWhile(cond, block):
                    label_head, label_body, label_end = (
                        self.fresh_label(),
                        self.fresh_label(),
                        self.fresh_label(),
                    )
                    code += (
                        [label_head]
                        + self.tmm_bool_code(cond, label_body, label_end)
                        + [label_body]
                        + self.tmm_block(block)
                        + [TACOp("jmp", [label_head], None)]
                        + [label_end]
                    )
                case StatementIf(cond, thenblock, elseblock):
                    label_true, label_false, label_end = (
                        self.fresh_label(),
                        self.fresh_label(),
                        self.fresh_label(),
                    )
                    code += (
                        self.tmm_bool_code(cond, label_true, label_false)
                        + [label_true]
                        + self.tmm_block(thenblock)
                        + [TACOp("jmp", [label_end], None), label_false]
                    )
                    if elseblock is not None:
                        code += self.tmm_block(elseblock) + [label_end]
                    else:
                        code += [label_end]
        return code

    def tmm_bool_code(
        self, expr: Expression, lab_true: TACLabel, lab_false: TACLabel
    ) -> List[TACOp | TACLabel]:
        match expr:
            case ExpressionBinOp(
                "equals" | "notequals" | "lt" | "lte" | "gt" | "gte" as op,
                left,
                right,
                _,
            ):
                left_tmp = self.fresh_temp()
                right_tmp = self.fresh_temp()
                left_ops = self.tmm_int_code(left, left_tmp)
                right_ops = self.tmm_int_code(right, right_tmp)
                match op:
                    case "equals":
                        return (
                            left_ops
                            + right_ops
                            + [
                                TACOp("sub", [left_tmp, right_tmp], left_tmp),
                                TACOp("jz", [left_tmp, lab_true], None),
                                TACOp("jmp", [lab_false], None),
                            ]
                        )
                    case "notequals":
                        return (
                            left_ops
                            + right_ops
                            + [
                                TACOp("sub", [left_tmp, right_tmp], left_tmp),
                                TACOp("jz", [left_tmp, lab_false], None),
                                TACOp("jmp", [lab_true], None),
                            ]
                        )
                    case x:
                        return (
                            left_ops
                            + right_ops
                            + [
                                TACOp("sub", [left_tmp, right_tmp], left_tmp),
                                TACOp(
                                    f"{COMPARISON_TOJMPCODE[x]}",
                                    [left_tmp, lab_true],
                                    None,
                                ),
                                TACOp("jmp", [lab_false], None),
                            ]
                        )
            case ExpressionBinOp("boolean-and", left, right, _):
                iterim_label = self.fresh_label()
                return (
                    self.tmm_bool_code(left, interim_label, lab_false)
                    + [interim_label]
                    + self.tmm_bool_code(right, lab_true, lab_false)
                )
            case ExpressionBinOp("boolean-or", left, right, _):
                iterim_label = self.fresh_label()
                return (
                    self.tmm_bool_code(
                        left,
                        lab_true,
                        interim_label,
                    )
                    + [interim_label]
                    + self.tmm_bool_code(right, lab_true, lab_false)
                )
            case ExpressionUniOp("boolean-negation", arg, _):
                return self.tmm_bool_code(expr, lab_false, lab_true)
            case x:
                print(f"Cannot ast2tac the expression: {x}")

    def tmm_int_code(self, expr: Expression, result: TACTemp) -> List[TACOp]:
        match expr:
            case ExpressionVar(name):
                return [TACOp("copy", [self.var_to_tmp[name]], result)]
            case ExpressionInt(val):
                return [TACOp("const", [val], result)]
            case ExpressionBinOp(operator, left, right):
                left_tmp = self.fresh_temp()
                right_tmp = self.fresh_temp()
                left_ops = self.tmm_int_code(left, left_tmp)
                right_ops = self.tmm_int_code(right, right_tmp)
                return (
                    left_ops
                    + right_ops
                    + [
                        TACOp(
                            OPERATOR_TO_OPCODE[operator], [left_tmp, right_tmp], result
                        )
                    ]
                )
            case ExpressionUniOp(operator, arg):
                tmp = self.fresh_temp()
                arg_op = self.tmm_int_code(arg, tmp)
                return arg_op + [TACOp(OPERATOR_TO_OPCODE[operator], [tmp], result)]
            case ExpressionCall("print", [arg]):
                tmp = self.fresh_temp()
                arg_op = self.tmm_int_code(arg, tmp)
                return arg_op + [TACOp("print", [tmp], None)]
            case x:
                raise ValueError(f"cant translate {x}")


COMPARISON_TOJMPCODE = {"lt": "jl", "lte": "jle", "gt": "jnle", "gte": "jnl"}

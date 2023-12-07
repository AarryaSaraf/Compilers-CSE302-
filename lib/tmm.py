from .bxast import *
from .tac import *
from typing import Dict, List


class TMM(Lowerer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.break_stack = []
        self.continue_stack = []

    def to_tac(self):
        return TAC(self.tmm_block(self.fn.body) + [TACOp("ret", [], None)])

    def tmm_block(self, block: Block) -> List[TAC]:
        code = []
        self.scope_stack.append({})
        for stmt in block.stmts:
            match stmt:
                case StatementAssign(var, expr):
                    code += self.tmm_int_code(expr, self.lookup_scope(var))
                case StatementEval(expr):
                    if isinstance(expr.ty, VoidType) and isinstance(
                        expr, ExpressionCall
                    ):
                        code += self.tmm_call(expr, None)
                    elif expr.ty == PrimiType("int"):
                        code += self.tmm_int_code(expr, None)
                    elif expr.ty == PrimiType("int"):
                        code += self.tmm_bool_code(expr, None, None)
                    else:
                        raise ValueError(f"cannot compile eval: {expr}")
                case StatementDecl(name, ty, init):
                    if ty == PrimiType("int"):
                        self.add_var(name)
                        code += self.tmm_int_code(init, self.lookup_scope(name))
                    if ty == PrimiType("bool"):
                        self.add_var(name)
                        var_tmp = self.lookup_scope(name)
                        lbl_true, lbl_false, lbl_end = (
                            self.fresh_label(),
                            self.fresh_label(),
                            self.fresh_label(),
                        )
                        code += self.tmm_bool_code(init, lbl_true, lbl_false) + [
                            lbl_true,
                            TACOp("const", [1], var_tmp),
                            TACOp("jmp", [lbl_end], None),
                            lbl_false,
                            TACOp("const", [0], var_tmp),
                            lbl_end,
                        ]
                case StatementWhile(cond, block):
                    label_head, label_body, label_end = (
                        self.fresh_label(),
                        self.fresh_label(),
                        self.fresh_label(),
                    )
                    self.continue_stack.append(label_head)
                    self.break_stack.append(label_end)
                    code += (
                        [label_head]
                        + self.tmm_bool_code(cond, label_body, label_end)
                        + [label_body]
                        + self.tmm_block(block)
                        + [TACOp("jmp", [label_head], None)]
                        + [label_end]
                    )
                    self.continue_stack.pop(-1)
                    self.break_stack.pop(-1)
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
                case StatementBreak():
                    code += [TACOp("jmp", [self.break_stack[0]], None)]
                case StatementContinue():
                    code += [TACOp("jmp", [self.continue_stack[0]], None)]
                case StatementBlock(block):
                    code += self.tmm_block(block)
                case StatementReturn(expr) if expr is not None:
                    if expr.ty == PrimiType("bool"):
                        lab_true, lab_false = self.fresh_label(), self.fresh_label()
                        code += self.tmm_bool_code(expr, lab_true, lab_false) + [
                            lab_true,
                            TACOp("ret", [1], None),
                            lab_false,
                            TACOp("ret", [0], None),
                        ]
                    else:
                        rettmp = self.fresh_temp()
                        code += self.tmm_int_code(expr, rettmp) + [
                            TACOp("ret", [rettmp], None)
                        ]
                case StatementReturn(None):
                    code += [TACOp("ret", [], None)]
        self.scope_stack = self.scope_stack[:-1]
        return code

    def tmm_call(self, callexpr: ExpressionCall, res: TACLabel):
        code = []
        arg_temps = []
        for argexpr in callexpr.arguments:
            tmp = self.fresh_temp()
            arg_temps.append(tmp)
            if argexpr.ty == PrimiType("int"):
                code += self.tmm_int_code(argexpr, tmp)
            else:
                # TODO: if argexpr is already a boolean var then we don't need this step
                lab_true, lab_false, lab_end = (
                    self.fresh_label(),
                    self.fresh_label(),
                    self.fresh_label(),
                )
                code += self.tmm_bool_code(argexpr, lab_true, lab_false) + [
                    lab_true,
                    TACOp("const", [1], tmp),
                    TACOp("jmp", [lab_end], None),
                    lab_false,
                    TACOp("const", [0], tmp),
                    lab_end,
                ]
        code += [TACOp("call", [callexpr.target]+ arg_temps , res)]
        return code

    def tmm_bool_code(
        self, expr: Expression, lab_true: TACLabel, lab_false: TACLabel
    ) -> List[TACOp | TACLabel]:
        match expr:
            case ExpressionCall():
                tmp = self.fresh_tmp()
                return self.tmm_call(expr, tmp) + [
                    TACOp("jz", [tmp, lab_false]),
                    TACOp("jmp", [lab_true]),
                ]

            case ExpressionBinOp(
                "equals" | "notequals" | "lt" | "lte" | "gt" | "gte" as op,
                left,
                right,
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
            case ExpressionBinOp("boolean-and", left, right):
                interim_label = self.fresh_label()
                return (
                    self.tmm_bool_code(left, interim_label, lab_false)
                    + [interim_label]
                    + self.tmm_bool_code(right, lab_true, lab_false)
                )
            case ExpressionBinOp("boolean-or", left, right):
                interim_label = self.fresh_label()
                return (
                    self.tmm_bool_code(
                        left,
                        lab_true,
                        interim_label,
                    )
                    + [interim_label]
                    + self.tmm_bool_code(right, lab_true, lab_false)
                )
            case ExpressionUniOp("boolean-negation", arg):
                return self.tmm_bool_code(arg, lab_false, lab_true)
            case ExpressionBool(True):
                return [TACOp("jmp", [lab_true], None)]
            case ExpressionBool(False):
                return [TACOp("jmp", [lab_false], None)]
            case ExpressionVar(x):
                return [
                    TACOp("jz", [self.lookup_scope(x), lab_false], None),
                    TACOp("jmp", [lab_true], None),
                ]
            case x:
                print(f"Cannot ast2tac the expression: {x}")

    def tmm_int_code(self, expr: Expression, result: TACTemp) -> List[TACOp]:
        match expr:
            case ExpressionVar(name):
                return [TACOp("copy", [self.lookup_scope(name)], result)]
            case ExpressionInt(val):
                return [TACOp("const", [val], result)]
            case ExpressionCall():
                return self.tmm_call(expr, result)
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

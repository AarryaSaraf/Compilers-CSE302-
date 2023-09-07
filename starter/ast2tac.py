from lib.tac import var_mapping, serialize
from lib.tmm import tmm
from lib.ast import deserialize
import json
import sys
from typing import List

#@dataclass
#class TACTemp:
#    num: int
#
#    def __str__(self):
#        return f"%{self.num}"
#
#@dataclass
#class TACOp:
#    opcode: str
#    args: List[TACTemp| int]
#    result: TACTemp| None
#
#    def to_dict(self):
#        return {
#            "opcode": self.opcode,
#            "args": [str(arg) for arg in self.args],
#            "result": str(self.result)
#        }
#
#def var_mapping(statements):
#    var_to_tmp = {}
#    for stmt in statements:
#        match stmt:
#            case StatementDecl(name, _, _): var_to_tmp[name] = fresh_temp()
#            case _: pass
#    return var_to_tmp
#
#
#
#def tmm(statments, var_to_tmp):
#    code = []
#    for stmt in statments:
#        match stmt: 
#            case StatementAssign(var, expr): code += tmm_code(expr, var_to_tmp[var], var_to_tmp)
#            case StatementEval(expr): code += tmm_code(expr, None, var_to_tmp)
#            case StatementDecl(name): code += [TACOp("const", [0], var_to_tmp[name])]
#    return code
#
#def tmm_code(expr, result, var_to_tmp) -> List[TACOp]:
#    match expr:
#        case ExpressionVar(name): 
#            return [TACOp("copy", [var_to_tmp[name]], result)]
#        case ExpressionInt(val):
#            return [TACOp("const", [val], result)]
#        case ExpressionBinOp(operator, left, right):
#            left_tmp = fresh_temp()
#            right_tmp = fresh_temp()
#            left_ops = tmm_code(left, left_tmp, var_to_tmp)
#            right_ops = tmm_code(right, right_tmp, var_to_tmp)
#            return left_ops + right_ops + [TACOp(operator, [left_tmp, right_tmp], result)]
#        case ExpressionUniOp(operator, arg):
#            tmp = fresh_temp()
#            arg_op = tmm_code(arg, tmp, var_to_tmp)
#            return arg_op + [TACOp(operator, [tmp], result)]
#        case ExpressionCall("print", [arg]):
#            tmp = fresh_temp()
#            arg_op = tmm_code(arg, tmp, var_to_tmp)
#            return arg_op + [TACOp("print", [tmp], None)]
#        case x:
#            raise ValueError(f"cant translate {x}")
#
#temporary_counter = 0
#
#def fresh_temp() -> TACTemp:
#    global temporary_counter
#    var = TACTemp(temporary_counter)
#    temporary_counter += 1
#    return var
#

def main(file):
    with open(file) as fp:
        js = json.load(fp)
    statements = deserialize(js)
    var_to_tmp = var_mapping(statements)
    return tmm(statements, var_to_tmp)
if __name__ == "__main__":
    print(main(sys.argv[1]))
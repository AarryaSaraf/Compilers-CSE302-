from .ast import *
from typing import Dict

@dataclass
class TACTemp:
    num: int

    def __str__(self):
        return f"%{self.num}"

@dataclass
class TACOp:
    opcode: str
    args: List[TACTemp| int]
    result: TACTemp| None

    def to_dict(self):
        return {
            "opcode": self.opcode,
            "args": [str(arg) if isinstance(arg, TACTemp) else arg for arg in self.args],
            "result": str(self.result) if isinstance(self.result, TACTemp) else self.result
        }

OPERATOR_TO_OPCODE={
    "addition": "add",
    "subtraction": "sub",
    "multiplication": "mul",
    "division": "div",
    "modulus": "mod",
    "bitwise-xor": "xor",
    "bitwise-or": "or",
    "bitwise-and": "and",
    "opposite": "neg",
    "bitwise-negation": "not"
}
temporary_counter = 0

def fresh_temp() -> TACTemp:
    global temporary_counter
    var = TACTemp(temporary_counter)
    temporary_counter += 1
    return var

def var_mapping(statements: List[Statement]) -> Dict[str, TACTemp]:
    var_to_tmp = {}
    for stmt in statements:
        match stmt:
            case StatementDecl(name, _, _): var_to_tmp[name] = fresh_temp()
            case _: pass
    return var_to_tmp


def serialize(tacops: List[TACOp]):
    ops_list = [op.to_dict() for op in tacops]
    return [{"proc": "@main", "body": ops_list}]

def pretty_print(tacops: List[TACOp]) -> str:
    pp = ""
    for op in tacops:
        pp+= f"{op.result} = {op.opcode} {' '.join([arg for arg in op.args])}\n"
    return pp
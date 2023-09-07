from .ast import *

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
            "args": [str(arg) for arg in self.args],
            "result": str(self.result)
        }


temporary_counter = 0

def fresh_temp() -> TACTemp:
    global temporary_counter
    var = TACTemp(temporary_counter)
    temporary_counter += 1
    return var

def var_mapping(statements):
    var_to_tmp = {}
    for stmt in statements:
        match stmt:
            case StatementDecl(name, _, _): var_to_tmp[name] = fresh_temp()
            case _: pass
    return var_to_tmp


def serialize(tacops):
    pass
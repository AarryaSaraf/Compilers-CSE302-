from typing import List
from .tac import *

@dataclass
class BasicBlock:
    entry: List[TACLabel]
    ops: List[TACOp]
    def append(self, op: TACOp):
        self.ops.append(inst)

def infer_basic_blocks(tac: TAC) -> List[BasicBlock]:
    blocks = []
    current_block = None
    match tac.ops[0]:
        case TACLabel(x) as lbl: current_block = BasicBlock(entry=lbl, inst=[])
        case _: raise ValueError(f"Instruction list must start with entry label")
    for op in tac.ops:
        opcode = op.opcode
        match opcode
from typing import Set
from .tac import *
from .cfg import *


class LivenessAnalyzer:
    def __init__(self, cfg: List[BasicBlock]) -> None:
        self.cfg = cfg
        self.edges_covered: Set[Tuple[TACLabel, TACLabel]]= set()

    def liveness_inst(self, live_out: Set[TACTemp], inst:TACOp):
        inst.live_out = inst.live_out.union(live_out)
        inst.live_in = inst.live_in.union(live_out)
        for arg in inst.args:
            if isinstance(arg, TACTemp):
                inst.live_in.add(arg)
        if inst.result is not None and inst.result in inst.live_in:
            inst.live_in.remove(inst.result)
        return inst.live_in
    
    def liveness_block(self, live_out: Set[TACTemp], block: BasicBlock):
        block.live_out = block.live_out.union(live_out)
        for inst in reversed(block.ops):
            live_out = self.liveness_inst(live_out, inst)
        block.live_in = block.live_in.union(live_out)
        
        for pred in block.predecessors:
            if (block.entry, pred.entry) not in self.edges_covered:
                self.liveness_block(live_out, pred)
                self.edges_covered.add((block.entry, pred.entry))
        
    
    def liveness(self):
        for block in self.cfg:
            if block.final():
                self.liveness_block(set(), block)
    
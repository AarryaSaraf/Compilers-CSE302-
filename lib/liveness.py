from typing import Set
from .tac import *
from .cfg import *
from .ssa import *

class LivenessAnalyzer:
    def __init__(self, cfg: List[BasicBlock]) -> None:
        self.cfg = cfg
        self.edges_covered: Set[Tuple[TACLabel, TACLabel]] = set()

    def liveness_inst(self, live_out: Set[TACTemp], inst: TACOp):
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
                self.edges_covered.add((block.entry, pred.entry))
                self.liveness_block(live_out, pred)

    def liveness(self):
        for block in self.cfg:
            if block.final():
                self.liveness_block(set(), block)


class SSALivenessAnalyzer:
    def __init__(self, ssaproc: SSAProc) -> None:
        self.ssaproc = ssaproc
        self.cfg = ssaproc.blocks
        self.edges_covered: Set[Tuple[TACLabel, TACLabel]] = set()
    
    def liveness_inst(self, live_out: Set[SSATemp], inst: SSAOp):
        inst.live_out = inst.live_out.union(live_out)
        inst.live_in = inst.live_in.union(live_out)
        inst.live_in  = inst.live_in.union(inst.use())
        if inst.result is not None and inst.result in inst.live_in:
            inst.live_in.remove(inst.result)
        return inst.live_in

    def liveness_block(self, live_out: Set[SSATemp], block: SSABasicBlock):
        block.live_out = block.live_out.union(live_out)
        for inst in reversed(block.ops):
            live_out = self.liveness_inst(live_out, inst)

        live_out_for_block = {}
        defined = set()
        for phi in block.defs:
            defined.add(phi.defined)
            for (lbl, tmp) in phi.sources.items():
                if lbl in live_out_for_block:
                    live_out_for_block[lbl].add(tmp)
                else:
                    live_out_for_block[lbl] = {tmp}
        block.live_in = live_out
        live_out = live_out - defined
        for pred in block.predecessors:
            if (block.entry, pred.entry) not in self.edges_covered:
                self.edges_covered.add((block.entry, pred.entry))
                if pred.entry in live_out_for_block:
                    self.liveness_block(live_out_for_block[pred.entry].union(live_out), pred)
                else:
                    self.liveness_block(live_out, pred)

    def liveness(self):
        for block in self.cfg:
            if block.final():
                self.liveness_block(set(), block)
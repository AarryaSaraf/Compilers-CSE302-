from ssa import *

class SCCPOptimizer:
    def __init__(self, ssaproc: SSAProc) -> None:
        self.proc = ssaproc
        self.eval = {block.entry: block.initial for block in ssaproc.blocks}
        self.vals = {var: "undef" for var in ssaproc.get_tmps()} | {param: "dyn" for param in ssaproc.params}
    
    def sccp_interate(self):
        for block in self.proc.blocks:
            if self.eval[block.entry]:
                self.sccp_block(block)
    
    def sccp_block(self, block: SSABasicBlock):
        jmp_ops = []
        for phi in block.defs:
            self.sccp_phi(phi)
        for inst in block.ops:
            if inst.opcode not in JMP_OPS:
                self.sccp_inst(inst)
            else:
                jmp_ops.append(inst)
        self.sccp_jumps(jmp_ops)         

    def sccp_inst(self, inst: SSAOp):
        pass
    
    def static(self, inst: SSAOp):
        return all([self.vals[v] not in ["undef", "dyn"] for v in inst.args if isinstance(v, SSAOp)])
    
    def sccp_jumps(self, jmp_ops: List[SSAOp]):
        pass

    def sccp_phi(self, phi: Phi):
        source_vals = [self.vals[v] for v in phi.sources.values()]
        computed_values = set([
            self.vals[v] for lbl, v in phi.sources.items() 
            if self.eval[lbl]
        ]) - {"undef", "dyn"}
        if len(set(source_vals) - {"undef", "dyn"}) > 1:
            self.vals[phi.defined] = "dyn"
        elif (True, "dyn") in [(self.eval[lbl],self.vals[v]) for lbl, v in phi.sources.items()]:
            self.vals[phi.defined] = "dyn"
        elif len(computed_values) == 1:
            self.vals[phi.defined] = computed_values.pop()
from .ssa import *
from .tac import COND_JMP_OPS, JMP_OPS
from math import log2
STATIC_OPS = [    
    "mod",
    "div",
    "add",
    "sub",
    "mul",
    "and",
    "or",
    "xor",
    "not",
    "neg",
    "copy",
    "lshift",
    "rshift",
    "const"
]
DYN_OPS = [
    "call"
]

class SCCPOptimizer:
    def __init__(self, ssaproc: SSAProc) -> None:
        self.proc = ssaproc
        self.eval = {block.entry: block.initial for block in ssaproc.blocks}
        self.vals = {var: "undef" for var in ssaproc.get_tmps()} | {param: "dyn" for param in ssaproc.params}
        
    def optimize(self):
        old_eval = self.eval.copy()
        old_vals = self.vals.copy()
        self.sccp_iterate()
        while old_eval != self.eval or old_vals != self.vals:
            old_eval = self.eval.copy()
            old_vals = self.vals.copy()
            self.sccp_iterate()
        self.delete_blocks()
        self.replace_vals()
        self.delete_insts()
        return self.proc

    def replace_vals(self):
        for tmp, val in self.vals.items():
            if val not in ["dyn", "undef"]:
                self.proc.rename_var(tmp, val, replace_results=False)
        
    def delete_insts(self):
        self.proc.delete_setting_inst(set([key for key, val in self.vals.items() if val not in ["dyn", "undef"]]))

    def delete_blocks(self):
        self.proc.blocks = [block for block in self.proc.blocks if self.eval[block.entry]]
        for block in self.proc.blocks:
            block.predecessors = [block for block in block.predecessors if self.eval[block.entry]]
            block.successors = [block for block in block.successors if self.eval[block.entry]]

    def sccp_iterate(self):
        for block in self.proc.blocks:
            if self.eval[block.entry]:
                self.sccp_block(block)
    
    def sccp_block(self, block: SSABasicBlock):
        jmp_ops = []
        new_phis = []
        for phi in block.defs:
            if self.sccp_phi(phi):
                new_phis.append(phi)
        new_insts = []
        for inst in block.ops:
            if inst.opcode not in JMP_OPS:
                if self.sccp_inst(inst):
                    new_insts.append(inst)
            else:
                jmp_ops.append(inst)
        new_jumps = self.sccp_jumps(jmp_ops)      
        block.defs = new_phis
        block.ops = new_insts + new_jumps
        self.update_pred_succ(jmp_ops, block)

    def update_pred_succ(self, jmp_ops: List[SSAOp], block: SSABasicBlock):
        jmp_labels = [op.args[1] if op.opcode in COND_JMP_OPS else op.args[0] for op in jmp_ops if op.opcode != "ret"]
        # search for fallthrough 
        if jmp_ops[-1].opcode == "jmp":
            fallthrough_label = jmp_ops[-1].args[0]
        else:
            fallthrough_label = None
        new_succ = []
        for succ in block.successors:
            if succ.entry not in jmp_labels:
                succ.predecessors = [pred for pred in succ.predecessors if pred.entry != block.entry]
            else:
                new_succ.append(succ)
            if fallthrough_label is not None and fallthrough_label == succ.entry:
                block.fallthrough = succ
        block.successors = new_succ
        
    def sccp_inst(self, inst: SSAOp):
        if self.static(inst):
            match inst.opcode:
                case "add": self.vals[inst.result] = self.get_val(inst.args[0]) + self.get_val(inst.args[1])
                case "sub": self.vals[inst.result] = self.get_val(inst.args[0]) - self.get_val(inst.args[1])
                case "mul": self.vals[inst.result] = self.get_val(inst.args[0]) * self.get_val(inst.args[1])
                case "div": self.vals[inst.result] = self.get_val(inst.args[0]) // self.get_val(inst.args[1])
                case "mod": self.vals[inst.result] = self.get_val(inst.args[0]) % self.get_val(inst.args[1])
                case "and": self.vals[inst.result] = self.get_val(inst.args[0]) & self.get_val(inst.args[1])
                case "xor": self.vals[inst.result] = self.get_val(inst.args[0]) ^ self.get_val(inst.args[1])
                case "or": self.vals[inst.result] = self.get_val(inst.args[0]) | self.get_val(inst.args[1])
                case "rshift": self.vals[inst.result] = self.get_val(inst.args[0]) >> self.get_val(inst.args[1])
                case "lshift": self.vals[inst.result] = self.get_val(inst.args[0]) << self.get_val(inst.args[1])
                case "not": self.vals[inst.result] = ~self.get_val(inst.args[0]) 
                case "neg": self.vals[inst.result] = -self.get_val(inst.args[0])
                case "copy": self.vals[inst.result] = self.get_val(inst.args[0])
                case "const": self.vals[inst.result] = self.get_val(inst.args[0])
            return False # indicates that this instruction can be removed
        # a bunch of special rules
        elif inst.opcode == "sub" and inst.args[0] == inst.args[1]:
            self.vals[inst.result] = 0
        elif inst.opcode in  ["sub", "add"] and self.get_val(inst.args[1]) == 0:
            inst.opcode = "copy"
            inst.args = [inst.args[0]]
        elif inst.opcode == "add" and self.get_val(inst.args[0]) == 0:
            inst.opcode = "copy"
            inst.args = [inst.args[1]]
        elif inst.opcode in ["mul", "div"] and self.get_val(inst.args[1]) == 1:
            inst.opcode = "copy"
            inst.args = [inst.args[0]]
        elif inst.opcode == "mul" and self.get_val(inst.args[0]) == 1:
            inst.opcode = "copy"
            inst.args = [inst.args[1]]
        elif inst.opcode == "div" and log2(self.get_val(inst.args[1])).is_integer():
            inst.opcode = "rshift"
            inst.args = [inst.arg[0], int(log2(self.get_val(inst.args[1])))]
        elif inst.opcode == "mul" and log2(self.get_val(inst.args[1])).is_integer():
            inst.opcode = "lshift"
            inst.args = [inst.arg[0], int(log2(self.get_val(inst.args[1])))]
        elif inst.opcode == "mul" and log2(self.get_val(inst.args[0])).is_integer():
            inst.opcode = "lshift"
            inst.args = [inst.arg[0], int(log2(self.get_val(inst.args[0])))]
        elif self.dynamic(inst):
            self.vals[inst.result] = "dyn"
        return True
    def static(self, inst: SSAOp):
        return inst.opcode in STATIC_OPS and all([self.get_val(v) not in ["undef", "dyn"] for v in inst.args]) and isinstance(inst.result, SSATemp)
    
    def dynamic(self, inst: SSAOp):
        return inst.opcode in DYN_OPS or any(self.get_val(var) == "dyn" for var in inst.args)
    
    def sccp_jumps(self, jmp_ops: List[SSAOp]):
        new_jmp_ops = []
        for jmp in jmp_ops:
            match jmp.opcode:
                case "ret": 
                    new_jmp_ops.append(jmp)
                case code if code in COND_JMP_OPS and self.get_val(jmp.args[0]) == "dyn": 
                    new_jmp_ops.append(jmp)
                    self.eval[jmp.args[1]] = True
                case code if code in COND_JMP_OPS and self.get_val(jmp.args[0]) == "undef": 
                    new_jmp_ops = jmp_ops
                    break
                case "jz" if self.get_val(jmp.args[0]) == 0: 
                    self.eval[jmp.args[1]] = True 
                    new_jmp_ops.append(SSAOp("jmp", [jmp.args[1]], None))
                    break
                case "jnz" if self.get_val(jmp.args[0]) != 0: 
                    self.eval[jmp.args[1]] = True 
                    new_jmp_ops.append(SSAOp("jmp", [jmp.args[1]], None))
                    break
                case "jl" if self.get_val(jmp.args[0]) < 0: 
                    self.eval[jmp.args[1]] = True 
                    new_jmp_ops.append(SSAOp("jmp", [jmp.args[1]], None))
                    break
                case "jle" if self.get_val(jmp.args[0]) <= 0: 
                    self.eval[jmp.args[1]] = True 
                    new_jmp_ops.append(SSAOp("jmp", [jmp.args[1]], None))
                    break
                case "jnl" if self.get_val(jmp.args[0]) >= 0: 
                    self.eval[jmp.args[1]] = True 
                    new_jmp_ops.append(SSAOp("jmp", [jmp.args[1]], None))
                    break
                case "jnle" if self.get_val(jmp.args[0]) > 0: 
                    self.eval[jmp.args[1]] = True 
                    new_jmp_ops.append(SSAOp("jmp", [jmp.args[1]], None))
                    break
                case "jmp":
                    self.eval[jmp.args[0]] = True 
                    new_jmp_ops.append(jmp)
                    break
        return new_jmp_ops

    def sccp_phi(self, phi: Phi):
        source_vals = [self.get_val(v) for v in phi.sources.values()]
        computed_values = set([
            self.get_val(v) for lbl, v in phi.sources.items() 
            if self.eval[lbl]
        ])
        if len(set(source_vals) - {"undef", "dyn"}) > 1:
            self.vals[phi.defined] = "dyn"
            return True
        elif (True, "dyn") in [(self.eval[lbl],self.get_val(v)) for lbl, v in phi.sources.items()]:
            self.vals[phi.defined] = "dyn"
            return True
        elif "dyn" not in source_vals and "undef" not in source_vals and len(computed_values) == 1:
            self.vals[phi.defined] = computed_values.pop()
            return False
        return True
        
    def get_val(self, var: SSATemp | TACGlobal):
        if isinstance(var, TACGlobal):
            return "dyn"
        elif isinstance(var, int) or isinstance(var, bool):
            return var
        else:
            return self.vals[var]
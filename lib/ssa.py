from .tac import *
from .cfg import BasicBlock
from .asmgen import CC_REG_ORDER
from typing import Any, Set
from copy import deepcopy

CC_REG_ORDER = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"] # used for dummy interference variable

class SSATemp:
    def __init__(self, id: str | int, version: int) -> None:
        self.id = id
        self.version = version

    def __str__(self):
        return f"%{self.id}.{self.version}"

    def __repr__(self):
        return f"%{self.id}.{self.version}"

    def __eq__(self, __value: object) -> bool:
        return self.id == __value.id and self.version == __value.version

    def __hash__(self) -> int:
        return hash(self.id) + hash(self.version)


@dataclass
class SSALabel:
    name: str

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, __value: object) -> bool:
        return __value.name == self.name

    def __str__(self):
        return f"%{self.name}"


@dataclass
class SSAGlobal:
    name: str

    def __str__(self) -> str:
        return f"@{self.name}"

    def __eq__(self, __value: object) -> bool:
        return self.name == __value.name


@dataclass
class SSAOp:
    opcode: str
    args: List[SSATemp | SSALabel | int | SSAGlobal]
    result: SSATemp | SSAGlobal | None

    live_in: Set[SSATemp] = field(default_factory=set)
    live_out: Set[SSATemp] = field(default_factory=set)

    def to_dict(self):
        return {
            "opcode": self.opcode,
            "args": [
                str(arg) if isinstance(arg, TACTemp) else arg for arg in self.args
            ],
            "result": str(self.result)
            if isinstance(self.result, TACTemp)
            else self.result,
        }

    def pretty(self):
        if self.result is not None:
            return f"{self.result} = {self.opcode} {' '.join([str(arg) for arg in self.args])}"
        return f"{self.opcode} {' '.join([str(arg) for arg in self.args])}"

    def detailed(self) -> str:
        return f"\t{str(self.live_in)} \n\t{self.pretty()}\n \t{str(self.live_out)}"
    
    def is_jmp(self) -> bool:
        return self.opcode in JMP_OPS

    def use(self,interference=False) -> Set[SSATemp]:
        used = {tmp for tmp in self.args if isinstance(tmp, SSATemp)}
        if interference:
            # these dummies only need to be added for the construction of the interference graph
            used = used.union(self.prealloc_dummies())
        return used
    
    def defined(self, interference=False) -> Set[SSATemp]:
        defined = set()
        
        if self.result is not None:
            defined.add(self.result)
        if interference:
            # these dummies only need to be added for the construction of the interference graph
            defined = defined.union(self.prealloc_dummies())
        return defined

    def prealloc_dummies(self):
        dummies = set()
        if self.opcode in ["div", "mod"]:
            dummies.add(SSATemp("%%rax", 0))
            dummies.add(SSATemp("%%rbx", 0))
            dummies.add(SSATemp("%%rdx", 0))
        elif self.opcode in ["shl", "shr"]:
            dummies.add(SSATemp("%%rcx", 0))
        elif self.opcode == "param" and self.args[0] < 7: # deprecated
            dummies.add(SSATemp(f"%%{CC_REG_ORDER[self.args[0]-1]}", 0))
        elif self.opcode == "call":
            dummies = dummies.union(set([SSATemp(f"%%{reg}", 0) for reg in CC_REG_ORDER[:len(self.args)-1]]))
        return dummies
    
@dataclass
class Phi:
    defined: SSATemp
    sources: Dict[SSALabel, SSATemp]

    def pretty(self):
        sourcespretty = " ".join(
            [f"{lbl.name}:{tmp}" for lbl, tmp in self.sources.items()]
        )
        return f"{self.defined} = \u03D5 {sourcespretty}"


@dataclass
class SSABasicBlock:
    entry: SSALabel
    defs: List[Phi]
    ops: List[SSAOp] = field(default_factory=list)
    successors: Set[Any] = field(default_factory=set)
    predecessors: Set[Any] = field(default_factory=set)
    versions_out: Dict[TACTemp, SSATemp] | None = None
    initial: bool = False
    fallthrough: Any | None = None

    # for liveness analysis
    live_in: Set[SSATemp] = field(default_factory=set)
    live_out: Set[SSATemp] = field(default_factory=set)

    def final(self) -> bool:
        return self.ops[-1].opcode == "ret"

    def empty(self) -> bool:
        return all([op.opcode in JMP_OPS for op in self.ops])


class SSACrudeGenerator:
    def __init__(self, blocks: List[BasicBlock], proc: TACProc) -> None:
        self.proc = proc
        self.blocks = blocks
        self.initial = [block for block in blocks if block.initial][0]
        self.current_version = {}
        self.converted_blocks = {}

    def to_ssa(self):
        # this converts everything into basic SSA with Phony defs that will be turned into phi functions in step2
        ssa_blocks = []
        for block in self.blocks:
            block = self.insert_phony(block)
            ssa_blocks.append(self.versioning(block))
        self.update_pred_succ(ssa_blocks)
        for block in ssa_blocks:
            self.convert_phony_to_phi(block)
        return ssa_blocks

    def insert_phony(self, block: BasicBlock):
        new_block = BasicBlock(
            deepcopy(block.entry),
            deepcopy(block.ops),
            block.successors,
            block.predecessors,
            block.initial,
            block.fallthrough,
            deepcopy(block.live_in),
            deepcopy(block.live_out),
        )
        phony_defs = []
        for tmp in block.live_in:
            phony_defs.append(TACOp("phony", [], tmp))
        new_block.ops = phony_defs + block.ops
        return new_block

    def convert_op(self, op: TACOp) -> SSAOp:
        args_versioned = [
            self.current_version[arg] if isinstance(arg, TACTemp) else arg
            for arg in op.args
        ]
        if op.result is not None:
            self.inc_version(op.result)
            result_versioned = self.current_version[op.result]
        else:
            result_versioned = None
        new_op = SSAOp(
            op.opcode,
            args_versioned,
            result_versioned,
        )
        return new_op
    
    def versioning(self, block: BasicBlock) -> SSABasicBlock:
        new_ops = []
        # I don't know about this... No this should be set from the phis
        for op in block.ops:
            new_op = self.convert_op(op)
            new_ops.append(new_op)
        return SSABasicBlock(
            block.entry,
            [],  # will be set later
            new_ops,
            block.successors,
            block.predecessors,
            initial=block.initial,
            versions_out=self.current_version.copy(),
        )

    def update_pred_succ(self, blocks: List[SSABasicBlock]):
        # this has to be done because the old blocks still poitn to TACBasicBlocks...
        label_to_ssablock = {block.entry: block for block in blocks}
        for block in blocks:
            block.predecessors = [
                label_to_ssablock[pred.entry] for pred in block.predecessors
            ]
            block.successors = [
                label_to_ssablock[succ.entry] for succ in block.successors
            ]
            if block.fallthrough is not None:
                block.fallthrough = label_to_ssablock[block.fallthrough.entry]

    def convert_phony_to_phi(self, block: SSABasicBlock) -> SSABasicBlock:
        defs = [op for op in block.ops if op.opcode == "phony"]
        non_defs = block.ops[len(defs) :]
        if block.initial:
            pass  # Figure out how to handle function parameters
        else:
            phis = [
                Phi(
                    phony.result,
                    {
                        pred.entry: pred.versions_out[TACTemp(phony.result.id)]
                        for pred in block.predecessors
                    },
                )
                for phony in defs
            ]
            block.defs = phis
        block.ops = non_defs

    def inc_version(self, tmp: TACTemp):
        if tmp in self.current_version:
            self.current_version[tmp] = SSATemp(
                tmp.id, self.current_version[tmp].version + 1
            )
        else:
            self.current_version[tmp] = SSATemp(tmp.id, 0)


class SSAOptimizer:
    def __init__(self, blocks: List[SSABasicBlock]) -> None:
        self.blocks = blocks

    def optimize(
        self, copy_propagate=True, rename_and_dead_choice=True
    ) -> List[SSABasicBlock]:
        if copy_propagate:
            self.copy_propagate()
        if rename_and_dead_choice:
            self.rename_simpl()
            self.no_choice_elim()
        return self.blocks

    def copy_propagate_block(self, block: SSABasicBlock):
        copy_continuations = {}
        new_ops = []
        for op in block.ops:
            if op.opcode == "copy":
                copy_continuations[op.result] = op.args[0]
                self.rename_var(op.result, op.args[0])
            else:
                new_ops.append(op)
        block.ops = new_ops

    def copy_propagate(self):
        for block in self.blocks:
            self.copy_propagate_block(block)

    def rename_var(self, old, new):
        for block in self.blocks:
            for phi in block.defs:
                phi.sources = {
                    lbl: new if tmp == old else tmp for lbl, tmp in phi.sources.items()
                }
                phi.defined = new if phi.defined == old else phi.defined
            for op in block.ops:
                op.args = [
                    new if isinstance(arg, SSATemp) and arg == old else arg
                    for arg in op.args
                ]
                op.result = (
                    new if op.result is not None and op.result == old else op.result
                )

    def rename_simpl(self):
        simpls = self.find_renames()
        while len(simpls) != 0:
            for old, new in simpls:
                self.rename_var(old, new)
            self.no_choice_elim()
            simpls = self.find_renames()

    def find_renames(self):
        renames = []
        for block in self.blocks:
            for phi in block.defs:
                unique_args = list(
                    set(phi.sources.values())
                )  # get unique values in the arguments
                if len(unique_args) == 1:
                    renames.append((phi.defined, unique_args[0]))
        return renames

    def no_choice_elim(self):
        for block in self.blocks:
            new_defs = []
            for phi in block.defs:
                if not all([phi.defined == arg for arg in phi.sources.values()]):
                    new_defs.append(phi)
            block.defs = new_defs

class SSADeconstructor:
    def __init__(self, blocks: List[SSABasicBlock]):
        self.blocks = blocks
        self.initial = [block for block in blocks if block.initial][0]
        self.already_serialized = set()
        self.serialization = []
        self.ssa_to_tac = {}
        self.dummy_counter = 0
        self.tactmp_counter = 0

    def ssatmp_to_tac(self, tmp: SSATemp) -> TACTemp:
        if tmp in self.ssa_to_tac:
            return self.ssa_to_tac[tmp]
        if isinstance(tmp.id, str) and tmp.version == 0:
            self.ssa_to_tac[tmp] = TACTemp(tmp.id)  # this is done for parameter passing
        else:
            self.ssa_to_tac[tmp] = TACTemp(self.tactmp_counter)
            self.tactmp_counter += 1
        return self.ssa_to_tac[tmp]
    
    def fresh_ssatmp(self):
        tmp = SSATemp(f"dummy", self.tactmp_counter)
        self.tactmp_counter += 1
        return tmp
    
    def ssaop_to_tac(self, op: SSAOp) -> TACOp:
        return TACOp(
            op.opcode,
            [
                self.ssatmp_to_tac(arg) if isinstance(arg, SSATemp) else arg
                for arg in op.args
            ],
            self.ssatmp_to_tac(op.result) if op.result is not None else None,
            live_in=op.live_in,
            live_out=op.live_out
        )

    def to_tac(self) -> TAC:
        self.resolve_phis()
        self.serialize(self.initial)
        self.rename_liveness_info()
        return TAC(self.serialization)

    def rename_liveness_info(self):
        for op in self.serialization:
            if isinstance(op, TACOp):
                op.live_in = {self.ssa_to_tac[tmp] for tmp in op.live_in}
                op.live_out = {self.ssa_to_tac[tmp] for tmp in op.live_out}

    def resolve_phis(self):
        copies_to_insert = {block.entry: set() for block in self.blocks}
        # gather the copies to be inserted
        for block in self.blocks:
            for phi in block.defs:
                for lab, tmp in phi.sources.items():
                    copies_to_insert[lab].add((phi.defined, tmp))
        # insert the copies
        for block in self.blocks:
            self.insert_copies(block, copies_to_insert[block.entry])
            
    def insert_copies(self, block, to_insert):
        # cylce detection
        breakups = self.detect_cycles(to_insert)
        dummy_copies = [
            TACOp("copy", [original], dummy)
            for (original, dummy) in breakups.items()
        ]
        copies = dummy_copies + [
            TACOp("copy", [breakups.get(src, src)], res)
            for (res, src) in to_insert
        ]
        print(dummy_copies)
        # TODO: add liveness
        live_out = set([c[0] for c in to_insert])
        for copy_inst in reversed(copies):
            copy_inst.live_out = live_out
            copy_inst.live_in = live_out.union(copy_inst.use())
            copy_inst.live_in.remove(copy_inst.result)
            live_out = copy_inst.live_in

        pre_jump = [op for op in block.ops if not op.is_jmp()]
        jumps = block.ops[len(pre_jump) :]
        block.ops = pre_jump + copies + jumps

    def detect_cycles(self, to_insert):
        used = set()
        defined = set()
        breakups = {}
        for res, src in to_insert:
            if res in used: # if we want to write to something used somewhere else
                breakups[res] = self.fresh_ssatmp()
            if src in defined:
                breakups[src] = self.fresh_ssatmp()
            if src not in breakups: # add every read to a variable that is not already broken up
                used.add(src)
            if res not in breakups:
                defined.add(res)
        return breakups
            
                
    def serialize(self, block: SSABasicBlock) -> TAC:
        if block.entry in self.already_serialized:
            return
        self.already_serialized.add(block.entry)
        self.serialization.append(block.entry)
        self.serialization += [self.ssaop_to_tac(op) for op in block.ops]
        if block.fallthrough is not None:
            self.serialize(block.fallthrough)
        for succ in block.successors:
            self.serialize(succ)

    def rename_alloc(self, alloc_mapping):
        return {self.ssatmp_to_tac(tmp): slot for tmp, slot in alloc_mapping.items()}

def ssa_print(block: SSABasicBlock):
    print(str(block.entry) + ":")
    for phi in block.defs:
        print("\t" + phi.pretty())
    for op in block.ops:
        if isinstance(op, SSAOp):
            print(f"\t{op.pretty()}")
        else:
            print(f"{op.name}")

def ssa_print_detailed(block: SSABasicBlock):
    print(str(block.entry) + ":")
    for phi in block.defs:
        print("\t" + phi.pretty())
    for op in block.ops:
        if isinstance(op, SSAOp):
            print(op.detailed())
        else:
            print(f"{op.name}")
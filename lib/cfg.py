from typing import List, Any
from dataclasses import field
from .tac import *

mutex_jmps = [
    ("jz", "jnz"),
    ("jz", "jl"),
    ("jz", "jnle"),
    ("jnl", "jl"),
    ("jnle", "jle"),
]

@dataclass
class BasicBlock:
    entry: TACLabel
    ops: List[TACOp] = field(default_factory=list)
    successors: List[Any] = field(default_factory=list)
    predecessors: List[Any] = field(default_factory=list)
    initial: bool = False
    fallthrough: TACLabel | None = None

    def empty(self)->bool:
        return all([op.opcode in JMP_OPS for op in self.ops])
    
    def successor_labels(self):
        lbls = []
        for op in self.ops:
            match op:
                case TACOp("jmp", [lbl], None):
                    lbls.append(lbl)
                case TACOp(opcode, [_, lbl], None) if opcode in COND_JMP_OPS:
                    lbls.append(lbl)
        return lbls

    def replace_jumps(self, old_label, new_label):
        for op in self.ops:
            match op:
                case TACOp("jmp", [lbl]) if lbl == old_label:
                    op.args[0] = new_label
                case TACOp(opcode, [_, lbl]) if opcode in COND_JMP_OPS and lbl == old_label :
                    op.args[-1] = new_label

def coalesce_block(block1:BasicBlock, block2:BasicBlock):
    # assumes block1's last instruction is a jump instruction that can be removed
    return BasicBlock(
        entry=block1.entry,
        ops=block1.ops[:-1]+ block2.ops,
        successors=block2.successors,
        predecessors = block1.predecessors,
        initial=block1.initial,
        fallthrough=block2.fallthrough
    )

class CFGAnalyzer:
    def __init__(self):
        self.entry_label_counter = 0

    def fresh_entry_label(self):
        lbl = TACLabel(f".Lentry{self.entry_label_counter}")
        self.entry_label_counter += 1
        return lbl

    def insert_labels(self, ops: List[TACOp | TACLabel]) ->List[TACOp | TACLabel]:
        new_ops = []
        if not isinstance(ops[0], TACLabel):
            new_ops = [self.fresh_entry_label()]

        for i, op in enumerate(ops):
            new_ops.append(op)
            match op:
                case TACOp(opcode, _, _) if opcode in JMP_OPS:
                    if i +1 < len(ops) and not isinstance(ops[i + 1], TACLabel):
                        new_ops.append(self.fresh_entry_label())
        return new_ops

    def split_blocks(self, ops: List[TACOp | TACLabel]) -> List[BasicBlock]:
        blocks = []
        block = BasicBlock(entry=ops[0], ops=[])
        for op in ops[1:]:
            match op:
                case TACLabel(_):
                    blocks.append(block)
                    block = BasicBlock(entry=op)
                case _:
                    block.ops.append(op)
        blocks.append(block)
        return blocks

    def add_fallthroughs(self, blocks):
        for block, following in zip(blocks[:-1], blocks[1:]):
            if (
                len(block.ops) == 0
                or (block.ops[-1].opcode != "jmp"
                and block.ops[-1].opcode != "ret")
            ):
                block.ops.append(TACOp("jmp", [following.entry], None))

    def get_blocks(self, ops: List[TACOp | TACLabel]) -> List[BasicBlock]:
        ops = self.insert_labels(ops)
        blocks = self.split_blocks(ops)
        self.add_fallthroughs(blocks)
        return blocks

    def lookup_block(self, label, blocks):
        for block in blocks:
            if block.entry == label:
                return block

    def cfg(self, blocks) -> BasicBlock:
        blocks[0].initial = True
        for block in blocks:
            successor_labels = block.successor_labels()
            successors = [self.lookup_block(lbl, blocks) for lbl in successor_labels]
            block.successors = successors
            for succ in successors:
                succ.predecessors.append(block)
            if block.ops[-1].opcode == "jmp":
                block.fallthrough = self.lookup_block(block.ops[-1].args[0], blocks)
        blocks[0]
        return blocks[0]
    
    def coalesce_blocks(self, blocks: List[BasicBlock]) -> List[BasicBlock]:
        new_blocks = []
        len_before = -1
        while len_before != len(blocks):
            len_before = len(blocks)
            new_blocks = []
            coalesced = set()
            for block in blocks:
                if block.entry in coalesced:
                    continue
                if len(block.successors) == 1 and len(block.successors[0].predecessors) == 1:
                    coalesced.add(block.successors[0].entry)
                    new_blocks.append(coalesce_block(block, block.successors[0]))
                else:
                    new_blocks.append(block)
            blocks = new_blocks
        return blocks
    
    def jump_unc_thread(self, blocks: List[BasicBlock]):
        skippable_blocks = []
        for block in blocks:
            if len(block.successors) == 1 and block.empty():
                skippable_blocks.append(block)
        for skippable in skippable_blocks:
            end_skip = self.trace_jumps(skippable)
            for pred in skippable.predecessors:
                pred.replace_jumps(skippable.entry, end_skip.entry)
    
    def trace_jumps(self, block: BasicBlock) -> BasicBlock:
        trace = block
        while len(trace.successors) == 1 and trace.empty():
            trace = trace.successors[0]
        return trace

    def optimize(self, tac: TAC) :
        blocks = self.get_blocks(tac.ops)
        self.cfg(blocks)
        self.jump_unc_thread(blocks)
        self.cfg(blocks)
        blocks = self.coalesce_blocks(blocks)
        self.cfg(blocks)
        initial = [block for block in blocks if block.initial][0]
        serializer = Serializer()
        return serializer.to_tac(initial)
    
    
class Serializer:

    def __init__(self) -> None:
        self.already_serialized = set()
        self.serialization: List[TACLabel| TACOp] = []

    def serialize(self, block: BasicBlock):
        if block.entry in self.already_serialized:
            return
        self.already_serialized.add(block.entry)
        self.serialization.append(block.entry)
        self.serialization += (block.ops)
        if block.fallthrough is not None:
            self.serialize(block.fallthrough)
        for succ in block.successors:
            self.serialize(succ)
        
    def to_tac(self, initial: Block) -> TAC:
        self.serialize(initial)
        return TAC(self.serialization)
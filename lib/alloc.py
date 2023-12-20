from .ssa import *
from .tac import *
from typing import List, Dict

CC_REG_ORDER = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]


class MemorySlot:
    pass


@dataclass
class AllocRecord:
    stacksize: int
    mapping: Dict[TACTemp | SSATemp, MemorySlot]


@dataclass
class Register(MemorySlot):
    name: str

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, Register) and self.name == __value.name


@dataclass
class StackSlot(MemorySlot):
    offset: int

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, StackSlot) and self.offset == __value.offset
    
@dataclass
class DataSlot(MemorySlot):
    name: str
    def __eq__(self, __value: object) -> bool:
         return isinstance(__value, DataSlot) and self.name == __value.name

@dataclass
class InterferenceGraphNode:
    tmp: SSATemp | TACTemp
    nbh: List[TACTemp | SSATemp]
    value: int = 0


@dataclass
class InterferenceGraph:
    nodes: Dict[SSATemp | TACTemp, InterferenceGraphNode]

    def __repr__(self):
        return str(self.nodes)

    def __str__(self):
        return str(self.nodes)

    def remove(self, tmp: SSATemp | TACTemp):
        """removes a node from the graph, used in register coalescing

        Args:
            tmp (SSATemp|TACTemp): the name of the node to be removed

        Returns:
            InterferenceGraph: New Graph without the removed node
        """
        del self.nodes[tmp]
        for i in list(self.nodes.keys()):
            node = self.nodes[i]
            if tmp in node.nbh:
                node.nbh.remove(tmp)
        return self

    def merge_nodes(self, new: SSATemp | TACTemp, old1: SSATemp | TACTemp, old2: SSATemp | TACTemp):
        """Merge nodes old1 and old2 into new (adding new), used in register coalescing.

        Args:
            new (Temp): temporary to be added
            a (Temp): temporary whos neighbours it copies
            b (Temp): temporary whos neighbours it copies

        Returns:
            _type_: _description_
        """
        nei = self.nodes[old1].nbh + self.nodes[old2].nbh
        self.nodes[new] = InterferenceGraphNode(new, nei, 0)
        return self



class Allocator:
    @abstractmethod
    def allocate(self) -> AllocRecord:
        pass


class SpillingAllocator(Allocator):
    def __init__(self, tacproc: TACProc) -> None:
        self.proc = tacproc

    def allocate(self) -> AllocRecord:
        params_reg_mapping = {
            param: Register(CC_REG_ORDER[i])
            for i, param in enumerate(self.proc.params[:6])
        }
        params_stack_mapping = {
            param: StackSlot(16 + (i) * 8)
            for i, param in enumerate(reversed(self.proc.params[6:]))
        }
        varlist = self.proc.body.get_tmps()
        var_mapping = {var: StackSlot(-(i + 1) * 8) for i, var in enumerate(varlist)}
        return AllocRecord(
            stacksize=len(var_mapping),
            mapping=params_reg_mapping | params_stack_mapping | var_mapping,
        )

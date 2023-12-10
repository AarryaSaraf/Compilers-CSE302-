from .ssa import *
from .tac import *
from typing import List, Dict

class MemorySlot:
    pass


@dataclass
class AllocRecord:
    stacksize: int
    mapping: Dict[TACTemp | SSATemp, MemorySlot]


@dataclass
class Register(MemorySlot):
    name: str

@dataclass
class StackSlot(MemorySlot):
    offset: int


@dataclass
class InterferenceGraphNode:
    tmp: SSATemp | TACTemp
    nbh: List[Any]
    value: int  = 0 
    
    def __repr__(self):
        return f"Tmp {self.tmp} nbh {self.nbh} value {self.value}."
    
    def __str__(self):
        return f"Tmp {self.tmp} nbh {self.nbh} value {self.value}."
@dataclass
class InterferenceGraph:
    nodes: Dict[SSATemp | TACTemp, List[InterferenceGraphNode]]
    
    def __repr__(self):
        return str(self.nodes)
    
    def __str__(self):
        return str(self.nodes)
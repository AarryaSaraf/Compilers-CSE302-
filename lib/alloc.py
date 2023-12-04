from .ssa import *
from .tac import *

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

@dataclass
class InterferenceGraph:
    nodes: List[InterferenceGraphNode]
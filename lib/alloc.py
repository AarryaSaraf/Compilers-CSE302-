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
class InterfernceGraphNode:
    tmp: SSATemp | TACTemp
    neighbors: List[Any]

@dataclass
class InferenceGraph:
    nodes: List[InterfernceGraphNode]
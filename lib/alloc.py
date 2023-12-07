from .ssa import *
from .tac import *

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

@dataclass
class StackSlot(MemorySlot):
    offset: int


@dataclass
class InterferenceGraphNode:
    tmp: SSATemp | TACTemp
    nbh: List[Any]
    value: int  = 0 


class Allocator:
    @abstractmethod
    def allocate(self) -> AllocRecord:
        pass

class SpillingAllocator(Allocator):
    def __init__(self, tacproc: TACProc) -> None:
        self.proc = tacproc
    
    def allocate(self) -> AllocRecord:
        params_reg_mapping = {param: Register(CC_REG_ORDER[i]) for i, param in enumerate(self.proc.params[:6])} 
        params_stack_mapping = {param: StackSlot(16+(i)*8) for i, param in enumerate(reversed(self.proc.params[6:]))} 
        varlist = self.proc.body.get_tmps()
        var_mapping={
            var: StackSlot(-(i+1)*8) for i, var in enumerate(varlist)
        }
        return AllocRecord(
            stacksize=len(var_mapping),
            mapping=params_reg_mapping | params_stack_mapping| var_mapping
        )

class InterferenceGraph:
    nodes: List[InterferenceGraphNode]

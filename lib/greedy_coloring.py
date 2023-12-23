import random
from .mcs import *
from .ssa import *
from .tac import *


color_map = (
    "%%rax",
    "%%rcx",
    "%%rdx",
    "%%rsi",
    "%%rdi",
    "%%r8",
    "%%r9",
    "%%r10",
    "%%rbx",
    "%%r12",
    "%%r13",
    "%%r14",
    "%%r15",
)
CC_REG_ORDER = ["%%rdi", "%%rsi", "%%rdx", "%%rcx", "%%r8", "%%r9"]

reg_map = {reg: color_map.index(reg) + 1 for reg in color_map}


def color_to_reg(col):
    return color_map[col - 1]


def reg_to_color(reg):
    return reg_map[reg]


def greedy_coloring(params: List[SSATemp], G: InterferenceGraph, elim: List[SSATemp]):
    """
    Parameters
    ----------
    params : list[temps]
        list of temps which store the parameters of the function
    G : interferance graph
    elim : list[temps]
        elimination ordering


    Returns
    -------
    dict
        the keys are temps
        the values are the assigned color (int)

    """

    K = len(elim)
    available_colors = [i + 1 for i in range(K)]
    col = {u: 0 for u in elim}
    # also I can handle it  if the params are not allocated to their CC registers
    for param, c in zip(params, CC_REG_ORDER):
        col[param] = reg_to_color(c)
        # I don't know why we would need to do this, we don't need to keep the params alive
        # available_colors.remove(col)

    # pre color the instruction specific interference dummies
    for u in elim:
        if str(u.id).startswith("%%"):
            col[u] = reg_to_color(u.id)

    for u in elim:
        if col[u] == 0:
            nei_colors = [col[nei] for nei in G.nodes[u].nbh]
            c = min([color for color in available_colors if color not in nei_colors])
            col[u] = c
    return col


def spill(col):
    """
    Parameters
    ----------
    col : dict
        the keys are temps
        the values are the assigned color (int)

    Returns
    -------
    temp | None

    """
    colors = set([col[u] for u in col.keys()])
    nb_colors = len(colors)
    if nb_colors <= 13:  # no need to spill
        return None
    else:
        maxi = max(colors)
        return random.choice([u for u in col.keys() if col[u] == maxi])


def allocate(params, G, elim):
    """

    Parameters
    ----------
    params : list[temps]
        list of temps which store the parameters of the function
    ret : temp
        temp where the return value of the proc is stored
    G : interferance graph
    elim: list[temps]
        elimination ordering
    Returns
    -------
    int, dict
        returns the stacksize and the alloc dic

    """

    col = greedy_coloring(params, G, elim)
    # the register coalsecing will mp go here
    to_spill = spill(col)
    spilled = []
    while to_spill is not None:
        spilled.append(to_spill)
        G.remove(to_spill)
        col = greedy_coloring(params, G, elim)
        to_spill = spill(col)
    stacksize = 8 * len(spilled)
    alloc = col
    for i, u in enumerate(spilled):
        alloc[u] = -(i + 1) * 8

    return stacksize, alloc


def free_color(graph: InterferenceGraph, coloring: Dict[SSATemp | TACTemp, int], tmp1: SSATemp | TACTemp, tmp2: SSATemp | TACTemp):
    """Check is whether a free color between tmp1 and tmp2  exists

    Args:
        G (InterfereneGraph): Interferene graph
        C (Dictionary SSATemp or TACTemp -> Int): Coloring
        tmp1 (SSATemp or TACTemp): The first temporary.
        tmp2 (SSATemp or TACTemp)

    Returns:
        bool or int: if it finds a free (register) color it returns its number. If not it returns false.
    """
    already_used = {coloring[tmp] for tmp in graph.nodes[tmp1].nbh + graph.nodes[tmp2].nbh}

    for i in range(1, len(color_map)+1):
        if i not in already_used:
            return i
    return False


# example from the lecture
G = {
    "a": ["d"],
    "d": ["a", "e", "c", "b"],
    "e": ["d", "c"],
    "c": ["b", "d", "e"],
    "b": ["d", "c"],
}

elim = ["b", "d", "c", "e", "a"]


class GraphAndColorAllocator:
    def __init__(self, ssa: SSAProc):
        """
        Args:
            ssa: An SSAProc to be allocated
        """
        self.proc = ssa
        self.blocks = ssa.blocks

    def allocate(self, coalesce_registers=True):
        """
        Produces a valid allocation
        Args:
            coalesce_registers (bool, optional): Whether to do register coalescing

        Returns:
            AllocRecord
        """
        # get the interference graph
        lout, de, use, cop = self.gather_liveness()
        ig = transformer(lout, de, use, cop)
        # compute elimination ordering
        seo = mcs(ig)
        stacksize, mapping = allocate(self.proc.params, ig, seo)
        
        if coalesce_registers:
            self.coalesce_registers(ig, mapping)
        mapping = {tmp: self.to_slot(alloc) for tmp, alloc in mapping.items()}
        # add locations for the stack parameters:
        for i, param in enumerate(reversed(self.proc.params[6:])):
            mapping[param] = StackSlot(16 + i * 8)
        return AllocRecord(
            stacksize,
            mapping=mapping
        )

    def gather_liveness(self):
        lout, de, use, cop = [], [], [], []
        for block in self.blocks:
            for op in block.ops:
                lout.append(list(op.live_out))
                de.append(list(op.defined(interference=True)))
                use.append(list(op.use(interference=True)))
                cop.append(op.opcode == "copy")
        return lout, de, use, cop

    def to_slot(self, i):
        if i >= 0:
            return Register(color_to_reg(i)[2:])
        else:
            return StackSlot(i)

    def coalesce_inst(
        self, inst: TACOp | SSAOp, ig: InterferenceGraph, coloring: Dict
    ) -> bool:
        """
        Performs register coalescing on TAC or SSA instructions.

        Args:
            inst (TACop or SSAOp): the instruction.
            ig (InterferenceGraph): an interference graph
            coloring (dict temp -> int): The current coloring
        Returns:
            bool: whether the instruction is to be removed
        """
        if inst.opcode == "copy" and isinstance(inst.result, SSATemp | TACTemp) and isinstance(inst.args[0], SSATemp | TACTemp):
            if coloring[inst.result] == coloring[inst.args[0]]:
                return True
            if inst.args[0] not in ig.nodes[inst.result].nbh:
                fc = free_color(ig, coloring, inst.args[0], inst.result)
                if fc:
                    new_tmp = self.proc.new_unused_tmp()
                    ig.merge_nodes(new_tmp, inst.result, inst.args[0])
                    ig.remove(inst.result)
                    ig.remove(inst.args[0])
                    coloring[new_tmp] = fc
                    self.proc.rename_var(old=inst.args[0], new=new_tmp)
                    self.proc.rename_var(old=inst.result, new=new_tmp)
                    return True
        return False

    def coalesce_registers(self, ig: InterferenceGraph, coloring: Dict):
        """
        Do register coalescing
        """
        # the main work is done in coalesce inst this just does it for
        for block in self.blocks:
            new_ops = []
            for op in block.ops:
                if not self.coalesce_inst(op, ig, coloring):
                    new_ops.append(op)
            block.ops = new_ops


class TACGraphAndColorAllocator(GraphAndColorAllocator):
    """
    Slight modification of the GraphAndCOlorAllocator to work with the deconstructed TAC
    """

    def __init__(self, tacproc: TACProc):
        self.proc = tacproc

    def gather_liveness(self):
        lout, de, use, cop = [], [], [], []
        for op in self.proc.body.ops:
            if isinstance(op, TACOp):
                lout.append(list(op.live_out))
                de.append(list(op.defined(interference=True)))
                use.append(list(op.use(interference=True)))
                cop.append(op.opcode == "copy")
        return lout, de, use, cop

    def coalesce_registers(self, ig: InterferenceGraph, coloring: Dict):
        new_ops = []
        for op in self.proc.body.ops:
            if not (isinstance(op, TACOp) and self.coalesce_inst(op, ig, coloring)):
                new_ops.append(op)
        self.proc.body.ops = new_ops

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
        G = remove(G, to_spill)
        col = greedy_coloring(params, G, elim)
        to_spill = spill(col)
    stacksize = 8 * len(spilled)
    alloc = {u: color_to_reg(col[u]) for u in col.keys()}
    for i, u in enumerate(spilled):
        alloc[u] = -(i + 1) * 8

    return stacksize, alloc


# generate colored graph
# then coalsecing
# then allocation


def rcol(G, C, cop):
    """register coalsecing changes instructions or merges registers

    Args:
        G (InterferenceGraph): IFGraph
        C (Dictionary tmp -> Int): Coloring
        cop (list of lists): each inner list contains a boolean (true if copy false if not, %a, %b where the instruction is %b = copy %a)
    """
    for b in cop:
        if b[0] and C[b[1]] == C[b[2]]:
            b = None
        elif b[1] not in G.nodes[b[2]].nbh:
            flag = free_color(G, C, b)
            if flag:
                flag -= 1
                tmp = TACTemp(flag, 0)
                G = adder(G, tmp, b[1], b[2])
                G = remove(G, b[1])
                G = remove(G, b[2])
                # replace  %a and %b with %c in the instruction space JONAS TO DO


def free_color(G, C, tmp1, tmp2):
    """Check is whether a free color between tmp1 and tmp2  exists

    Args:
        G (InterfereneGraph): Interferene graph
        C (Dictionary tmp -> Int): Coloring
        b ([bool, %a, %b]): 1 element of cop from the preious function

    Returns:
        _type_: False if no such c exists
                (c+1) if c exists. It is c+1 so it necessarily satisfies the if(c) conditional.
    """
    u = G.nodes[tmp1].nbh + G.nodes[tmp2].nbh
    col = []
    for i in u:
        col.append(C[i])
    flag = False
    for i in list(C.values()):
        if i not in col:
            flag = i + 1
    return flag


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
        return AllocRecord(
            stacksize,
            mapping={tmp: self.to_slot(alloc) for tmp, alloc in mapping.items()},
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
        if isinstance(i, str):
            return Register(i[2:])
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
        if inst.opcode == "copy" and not (isinstance(inst.args[0], TACGlobal) or isinstance(inst.result, TACGlobal)):
            if inst.result == inst.args[0]:
                return True
            if inst.args[0] not in ig.nodes[inst.result].nbh:
                fc = free_color(ig, coloring, inst.args[0], inst.result)
                if fc:
                    new_tmp = self.proc.new_unused_tmp()
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

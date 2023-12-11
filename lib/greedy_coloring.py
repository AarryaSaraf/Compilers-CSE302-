import random
from .mcs import *
from .ssa import *
from .tac import *


color_map = (
'%%rax', '%%rcx', '%%rdx', '%%rsi', '%%rdi', '%%r8', '%%r9', '%%r10',
'%%rbx', '%%r12', '%%r13', '%%r14', '%%r15'
)

reg_map = {reg: color_map.index(reg) + 1 for reg in color_map}
def color_to_reg(col): return color_map[col - 1]
def reg_to_color(reg): return reg_map[reg]


def greedy_coloring(params, ret, G, elim):

    """
    Parameters
    ----------
    params : list[temps]
        list of temps which store the parameters of the function
    ret : temp
        temp where the return value of the proc is stored
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
    print(available_colors)
    param_colors = [i for i in range(2, 8)] #the first one is rax, then we take from 2 to 2+6=8 for the param colors
    col = {u : 0 for u in elim}

    for u in elim:
        if u == ret:
            col[u] = 1
            available_colors.remove(1)
        for param in params:
            if param == u:
                col[u] = param_colors[0]
                param_colors.remove(col[u])
                available_colors.remove(col[u])

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
    if nb_colors <= 13: #no need to spill
        return None
    else:
        maxi = max(colors)
        return random.choice([u for u in col.keys() if col[u] == maxi])
    

def allocate(params, ret, G, elim):

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

    col = greedy_coloring(params, ret, G, elim)
    # the register coalsecing will mp go here
    to_spill = spill(col)
    spilled = []
    while to_spill is not None:
        spilled.append(to_spill)
        G = remove(G, to_spill)  
        col = greedy_coloring(params, ret, G, elim)
        to_spill = spill(col)
    stacksize = 8*len(spilled)
    alloc = {u : color_to_reg(col[u]) for u in col.keys()}
    for i, u in enumerate(spilled):
        alloc[u] = -(i+1)*8

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
        if(b[0] and C[b[1]] == C[b[2]]):
            b = None
        elif(b[1] not in G.nodes[b[2]].nbh):
            flag  = exc(G, C,b)
            if(flag):
                flag -=1
                tmp = TACTemp(flag, 0)
                G = adder(G, tmp, b[1], b[2])
                G = remove(G, b[1])
                G = remove(G, b[2])
                # replace  %a and %b with %c in the instruction space JONAS TO DO 
                
def exc(G, C, b):
    """ Check is such a c exists

    Args:
        G (InterfereneGraph): Interferene graph
        C (Dictionary tmp -> Int): Coloring
        b ([bool, %a, %b]): 1 element of cop from the preious function

    Returns:
        _type_: False if no such c exists
                (c+1) if c exists. It is c+1 so it necessarily satisfies the if(c) conditional.
    """
    u = G.nodes[b[1]].nbh + G.nodes[b[2]].nbh
    col = []
    for i in u:
        col.append(C[i])
    flag = False
    for i in list(C.values()):
        if i not in col:
            flag = (i+1)
    return flag
                
# example from the lecture
G = {'a': ['d'],
     'd': ['a', 'e', 'c', 'b'],
     'e': ['d', 'c'],
     'c': ['b', 'd', 'e'],
     'b': ['d', 'c'],
    }
    
elim = ['b', 'd', 'c', 'e', 'a']

class GraphAndColor():
    def __init__(self, lin, de, use, cop, ):
        """ 
        lin (list of list of SSATemps or TACTemps): live in
        de (list of list of SSATemps or TACTemps)): def
        use (list of list of SSATemps or TACTemps): use
        cop (list of Bool): copy or not. List of booleans
        
        """
        self.ig = transformer(lin,de,use,cop)
        self.seo = mcs(self.ig)
        
    def allocated(self, params, ret):
        """

        Args:
            params : list[temps]
        list of temps which store the parameters of the function
            ret : temp
        temp where the return value of the proc is stored

        Returns:
            dict temps -> int: values are the assigned color (int) 
        """
        return allocate((params, ret, self.ig, self.seo) )

        










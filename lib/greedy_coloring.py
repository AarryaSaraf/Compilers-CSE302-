import random
from .mcs import *

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

    Returns
    -------
    int, dict
        returns the stacksize and the alloc dic
    
    """

    col = greedy_coloring(params, ret, G, elim)
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


# example from the lecture
G = {'a': ['d'],
     'd': ['a', 'e', 'c', 'b'],
     'e': ['d', 'c'],
     'c': ['b', 'd', 'e'],
     'b': ['d', 'c'],
    }
    
elim = ['b', 'd', 'c', 'e', 'a']
















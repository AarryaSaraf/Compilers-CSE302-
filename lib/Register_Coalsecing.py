#Register Coalsecing
from .ssa import *
from .tac import *
from .mcs import *


# generate colored graph 
# then coalsecing
# then allocation

def rcol(G, C, cop):
    """register coalsecing

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
    u = G.nodes[b[1]].nbh + G.nodes[b[2]].nbh
    col = []
    for i in u:
        col.append(C[i])
    flag = False
    for i in list(C.values()):
        if i not in col:
            flag = (i+1)
    return flag
                
            
        
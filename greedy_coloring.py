color_map = (
'%%rax', '%%rcx', '%%rdx', '%%rsi', '%%rdi', '%%r8', '%%r9', '%%r10',
'%%rbx', '%%r12', '%%r13', '%%r14', '%%r15', '%%r11', '%%rbp', '%%rsp'
)
reg_map = {reg: color_map.index(reg) + 1 for reg in color_map}
def color_to_reg(col): return color_map[col - 1]
def reg_to_color(reg): return reg_map[reg]


def greedy_coloring(params, ret, G):

    """Params : list of arguments [1st, 2nd, 3rd, ...]
       Ret : returned temporary
       """

    col = {}
    available_colors = [i+1 for i in range(13)]
    param_colors = [i+1 for i in range(6)]

    V = [elem[0] for elem in input]

    for u in V:
        col[u] = 0
        if u == ret:
            col[u] = 7
            available_colors.remove(7)
        for param in params:
            if param == u:
                col[u] = param_colors[0]
                param_colors.remove(col[u])
                available_colors.remove(col[u])

    for u in V:
        if col[u] == 0:
            nei_colors = [col[nei] for nei in G[u]]
            c = min([color for color in available_colors if color not in nei_colors])
            if c == None:
                return []
            col[u] = c


    return [(u, color_to_reg(col[u])) for u in V]

    
        





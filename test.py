import sys
from typing import Dict
from lib.asmgen import AsmGen, make_data_section, make_text_section, global_symbs
from lib.parser import parser
from lib.tmm import TMM
from lib.tac import TACGlobal, TACProc, pretty_print, print_detailed
from lib.liveness import LivenessAnalyzer, SSALivenessAnalyzer
#from lib.cfg import CFGAnalyzer, Serializer
from lib.bxast import Function, StatementDecl
from lib.checker import SyntaxChecker, TypeChecker
from lib.ssa import SSACrudeGenerator, SSADeconstructor, ssa_print_detailed, SSAOptimizer


src = "examples/fib10.bx"
decls = parser.parse(src)
s_checker = SyntaxChecker()
errs = s_checker.check_program(decls)
if errs != []:
    s_checker.pp_errs(errs)
    sys.exit()
t_checker = TypeChecker()
type_check = t_checker.check(decls)
if len(type_check) > 0:
    print("Type checking failed")
    sys.exit()
globvars = [decl for decl in decls if isinstance(decl, StatementDecl)]
funs = [fun for fun in decls if isinstance(fun, Function)]
globalmap = {var.name: TACGlobal(var.name) for var in globvars}
symbs = global_symbs(decls)
data_section = make_data_section(globvars)

def get_liv(ast: Function, globalmap: Dict[str, TACGlobal]) -> str:
    lowerer = TMM(ast, globalmap)
    tacproc = lowerer.lower()
    cfg_analyzer = CFGAnalyzer(tacproc)
    blocks = cfg_analyzer.optimize()
    liveness_analyzer = LivenessAnalyzer(blocks)
    liveness_analyzer.liveness()
    ssa_gen = SSACrudeGenerator(blocks, tacproc)
    ssa_blocks = ssa_gen.to_ssa()

    ssa_optim = SSAOptimizer(ssa_blocks)
    ssa_blocks = ssa_optim.optimize()

    ssa_liveness_analyzer = SSALivenessAnalyzer(ssa_blocks)
    return ssa_liveness_analyzer


liveness_analyzers = [get_liv(fun, globalmap) for fun in funs]
print(liveness_analyzers)

"""

liveness_analyzer = SSALivenessAnalyzer(cfg)
liveness_analyzer.liveness()

# Dictionary to store minimum lifetime for each temporary
min_lifetime = {}

for block in liveness_analyzer.cfg:
    for temp in block.live_in.union(block.live_out):
        if temp not in min_lifetime:
            min_lifetime[temp] = float('inf')  # Initialize with infinity
        # Update minimum lifetime based on block entry and exit labels
        min_lifetime[temp] = min(min_lifetime[temp], block.entry, block.exit)

# Identify temporaries with the least lifetime
least_lifetime_temps = [temp for temp, lifetime in min_lifetime.items() if lifetime != float('inf') and lifetime == min(min_lifetime.values())]

# Print or further analyze the results
print("Temporaries with the least lifetime:", least_lifetime_temps)

"""
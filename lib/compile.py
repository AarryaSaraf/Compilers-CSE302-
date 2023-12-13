import sys
from typing import Dict
from .asmgen import AsmGen, make_data_section, make_text_section, global_symbs
from .parser import parser
from .tmm import TMM
from .tac import TACGlobal, TACProc, pretty_print, print_detailed
from .liveness import LivenessAnalyzer, SSALivenessAnalyzer
from .cfg import CFGAnalyzer, Serializer
from .bxast import Function, StatementDecl
from .checker import SyntaxChecker, TypeChecker
from .ssa import SSACrudeGenerator, SSADeconstructor, ssa_print_detailed, SSAOptimizer
from .asmgen2 import AllocAsmGen
from .alloc import SpillingAllocator, AllocRecord
from .greedy_coloring import GraphAndColorAllocator
def compile(src: str):
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
    text_section = make_text_section([compile_unit(fun, globalmap) for fun in funs])
    return symbs + data_section + text_section


def compile_unit(fun: Function, globalmap: Dict[str, TACGlobal], register_alloc=True) -> str:
    """
    Compiles a single function

    Args:
        fun (Fuction): the AST of the function
        globalmap (dict str -> TACGlobal): a mapping of global variables
        register_alloc (bool, optional): whether to do register allocation, defaults to True
    """
    lowerer = TMM(fun, globalmap)
    tacproc = lowerer.lower()
    cfg_analyzer = CFGAnalyzer(tacproc)
    blocks = cfg_analyzer.optimize()
    liveness_analyzer = LivenessAnalyzer(blocks)
    liveness_analyzer.liveness()
    ssa_gen = SSACrudeGenerator(blocks, tacproc)
    ssa_blocks = ssa_gen.to_ssa()

    ssa_optim = SSAOptimizer(ssa_blocks)
    ssa_blocks = ssa_optim.optimize(copy_propagate=False)

    ssa_liveness_analyzer = SSALivenessAnalyzer(ssa_blocks)
    ssa_liveness_analyzer.liveness()
    #print(fun.name)
    #for block in ssa_blocks:
    #    ssa_print_detailed(block)  
    graph_alloc = GraphAndColorAllocator(ssa_blocks, tacproc).allocate()
    #print(graph_alloc)
    serializer = SSADeconstructor(ssa_blocks)
    tacproc.body = serializer.to_tac()
    #print_detailed(tacproc.body)
    if register_alloc:
        #spilled_alloc = SpillingAllocator(tacproc).allocate()
        # this rename is somewhat ugly but has to be done here otherwise we get circular imports
        alloc = AllocRecord(
            graph_alloc.stacksize,
            serializer.rename_alloc(graph_alloc.mapping)
        )
        #print(alloc)
        asm_gen = AllocAsmGen(tacproc,alloc)
    else:
        asm_gen = AsmGen(tacproc)
    asm = asm_gen.compile()
    return asm

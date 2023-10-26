from .asmgen import AsmGen
from .parser import parser
from .checker import pp_errs, check_programm
from .tmm import TMM
from .cfg import CFGAnalyzer
from bxast import Function, StatementDecl


def compile(src: str):
    pass


def compile_unit(ast: Function, globals) -> str:
    lowerer = TMM(ast, globals)
    tac = lowerer.to_tac()

    cfg_analyzer = CFGAnalyzer()
    optim_tac = cfg_analyzer.optimize(tac)

    asm_gen = AsmGen(optim_tac)
    asm = asm_gen.compile()
    return asm


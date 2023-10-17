from .asmgen import AsmGen
from .parser import parser
from .checker import pp_errs, check_programm
from .tmm import TMM
from .cfg import CFGAnalyzer
from bxast import Function, StatementDecl

def compile(src: str):
    pass

def compile_unit(ast: Function | StatementDecl) -> str:
    if isinstance(ast, Function):
        type_check = ast.type_check()
        if not type_check:
            raise Exception("Type Checking Failed, see above")
        lowerer = TMM(ast)
        tac = lowerer.to_tac()

        cfg_analyzer = CFGAnalyzer()
        optim_tac = cfg_analyzer.optimize(tac)

        asm_gen = AsmGen(optim_tac)
        asm = asm_gen.compile()
        return asm
    else:
        raise NotImplementedError("Cannot compile globals yet")
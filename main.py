import sys
import os
from lib.asmgen import AsmGen
from lib.parser import parser
from lib.checker import SyntaxChecker, TypeChecker
from lib.tmm import TMM
from lib.cfg import CFGAnalyzer
from lib.tac import pretty_print
if __name__ == "__main__":
    sourcefile = sys.argv[1]
    #sourcefile= "examples/bigcondition2.bx"
    with open(sourcefile) as fp:
        source = fp.read()
    
    decls = parser.parse(source)
    ast = decls[0]
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

    lowerer = TMM(ast)
    tac = lowerer.to_tac()
    cfg_analyzer = CFGAnalyzer()
    optim_tac = cfg_analyzer.optimize(tac)

    asm_gen = AsmGen(optim_tac)
    asm = asm_gen.compile()


    if "--nolink" in sys.argv:
        print(asm)
    else:
        if "-o" in sys.argv:
            i = sys.argv.index("-o")
            output = sys.argv[i + 1]
        else:
            output = "out"
        #output = "examples/bigcond2_opt"
        fp = open(f"{output}.S", "w")
        fp.write(asm)
        fp.close()
        os.system(f"gcc -o {output}.o {output}.S bx_runtime.c")

import sys
import os
from lib.asmgen import AsmGen
from lib.parser import parser
from lib.checker import pp_errs, check_programm
from lib.tmm import TMM
from lib.cfg import CFGAnalyzer
if __name__ == "__main__":
    #sourcefile = sys.argv[1]
    sourcefile= "examples/collatz.bx"
    with open(sourcefile) as fp:
        source = fp.read()

    ast = parser.parse(source)
    errs = check_programm(ast)
    if errs != []:
        pp_errs(errs)
        sys.exit()

    type_check = ast.type_check()
    if not type_check:
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
        output = "examples/collatz"
        fp = open(f"{output}.S", "w")
        fp.write(asm)
        fp.close()
        os.system(f"gcc -o {output}.o {output}.S bx_runtime.c")

import sys
import os
from lib.asmgen import AsmGen
from lib.parser import parser
from lib.checker import pp_errs, check_programm
from lib.tmm import TMM

if __name__ == "__main__":
    sourcefile = sys.argv[1]
    #sourcefile= "examples/bigcondition1.bx"
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
    asm_gen = AsmGen(tac)
    asm = asm_gen.compile()
    if "--nolink" in sys.argv:
        print(asm)
    else:
        if "-o" in sys.argv:
            i = sys.argv.index("-o")
            output = sys.argv[i + 1]
        else:
            output = "out"
        # output = "examples/bigcond1"
        fp = open(f"{output}.S", "w")
        fp.write(asm)
        fp.close()
        os.system(f"gcc -o {output}.o {output}.S bx_runtime.c")

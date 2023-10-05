import sys
import os
from lib.asmgen import AsmGen
from lib.parser import parser
from lib.checker import pp_errs, check_programm
from lib.bmm import bmm
from lib.tac import var_mapping

if __name__ == "__main__":
    with open(sys.argv[1]) as fp:
        source = fp.read()
    ast = parser.parse(source)
    errs = check_programm(ast)
    if errs != []:
        pp_errs(errs)
        sys.exit()
    
    vars_to_tmp = var_mapping(ast.body.stmts)
    tac = bmm(ast.body.stmts, vars_to_tmp)

    asm_gen = AsmGen(tac)
    asm = asm_gen.compile()
    if "--nolink" in sys.argv:
        print(asm)
    else:
        if "-o" in sys.argv:
            i = sys.argv.index("-o")
            output = sys.argv[i+1]
        else:
            output = "out"
        fp = open(f"{output}.S", "w")
        fp.write(asm)
        fp.close()
        os.system(f"gcc -o {output}.o {output}.S bx_runtime.c")
        
    
import sys
import os
from lib.asmgen import AsmGen
from lib.parser import parser
from lib.checker import SyntaxChecker, TypeChecker
from lib.tmm import TMM
from lib.cfg import CFGAnalyzer
from lib.tac import pretty_print
from lib.compile import compile

if __name__ == "__main__":
    sourcefile = sys.argv[1]
    # sourcefile= "examples/bigcondition2.bx"
    with open(sourcefile) as fp:
        source = fp.read()

    asm = compile(source)

    if "--nolink" in sys.argv:
        print(asm)
    else:
        if "-o" in sys.argv:
            i = sys.argv.index("-o")
            output = sys.argv[i + 1]
        else:
            output = "out"
        # output = "examples/bigcond2_opt"
        fp = open(f"{output}.S", "w")
        fp.write(asm)
        fp.close()
        os.system(f"gcc -o {output}.o {output}.S bx_runtime.c")

from lib.parser import parser
from lib.scanner import lexer
from lib.checker import check_programm, pp_errs
import sys

if __name__ == "__main__":
    with open(sys.argv[1]) as fp:
        source = fp.read()
    ast = parser.parse(source)
    pp_errs(check_programm(ast))
    print(ast)

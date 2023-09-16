from lib.parser import parser
from lib.scanner import lexer
import sys
if __name__ == "__main__":
    with open(sys.argv[1]) as fp:
        source = fp.read()
    ast = parser.parse(source)
    print(ast)
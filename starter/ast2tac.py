from lib.tac import var_mapping, serialize, pretty_print
from lib.tmm import tmm
from lib.bmm import bmm
from lib.ast import deserialize
import json
import sys
from typing import List


def main(file, method="tmm"):
    with open(file) as fp:
        js = json.load(fp)
    statements = deserialize(js)
    var_to_tmp = var_mapping(statements)
    if method=="tmm":
        code = tmm(statements, var_to_tmp)
    else:
        code = bmm(statements, var_to_tmp)
    return pretty_print(code)

if __name__ == "__main__":
    method = "bmm" if "--bmm" in sys.argv else "tmm"
    print(main(sys.argv[1], method=method))
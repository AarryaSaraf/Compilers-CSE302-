from lib.tac import var_mapping, serialize, pretty_print
from lib.tmm import tmm
from lib.ast import deserialize
import json
import sys
from typing import List


def main(file):
    with open(file) as fp:
        js = json.load(fp)
    statements = deserialize(js)
    var_to_tmp = var_mapping(statements)
    return pretty_print(tmm(statements, var_to_tmp))
if __name__ == "__main__":
    print(main(sys.argv[1]))
from ast_helper import *
import json
import sys

def main(file):
    with open(file) as fp:
        js = json.load(fp)
    statements = deserialize(js)

    return statements

if __name__ == "__main__":
    print(main(sys.argv[1]))
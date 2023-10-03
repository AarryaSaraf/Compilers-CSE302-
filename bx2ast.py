#! /usr/bin/env python3

# ====================================================================
import sys, urllib.request

# ====================================================================
URL = "https://grader.dix.polytechnique.fr/bxserver/bx2ast"
# URL = "http://localhost:5000/bx2ast"

# ====================================================================
def _main():
    if len(sys.argv)-1 not in (1, 2):
        print(f'Usage: {sys.argv[0]} [FILE.bx] <OUTPUT.json>')
        exit(1)

    filename, output = sys.argv[1], None

    if len(sys.argv)-1 == 2:
        output = sys.argv[2]

    with open(filename, 'r') as stream:
        contents = stream.read()

    request = urllib.request.Request(URL)

    request.add_header('Accept'        , 'application/json')
    request.add_header('Content-Type'  , 'text/plain; charset=utf-8')
    request.add_header('Content-Length', str(len(contents)))

    with urllib.request.urlopen(request, contents.encode('utf-8')) as response:
        ast = response.read()
        enc = response.info().get_param('charset') or 'utf-8'
        
    ast = ast.decode('utf-8')

    if output is None:
        sys.stdout.write(ast)
    else:
        with open(output, 'w', encoding = 'utf-8') as stream:
            stream.write(ast)

# ====================================================================
if __name__ == '__main__':
    _main()

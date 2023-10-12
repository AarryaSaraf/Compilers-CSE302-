import ply.lex as lex

reserved = {
    "def": "DEF",
    "var": "VAR",
    "print": "PRINT",
    "int": "INT",
    "if": "IF",
    "while": "WHILE",
    "else": "ELSE",
    "true": "TRUE",
    "false": "FALSE",
    "break": "BREAK",
    "continue": "CONTINUE",
}
tokens = (
    "IDENT",
    "NUMBER",
    "TRUE",
    "FALSE",
    "MAIN",
    "LPAREN",
    "RPAREN",
    "VAR",
    "EQUALS",
    "COLON",
    "SEMICOLON",
    "PRINT",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "MOD",
    "AND",
    "OR",
    "XOR",
    "LSHIFT",
    "RSHIFT",
    "TILDE",
    "COMMENT",
    "LBRACE",
    "RBRACE",
    "INT",
    "DEF",
    "EQUALSEQUALS",
    "NOTEQUALS",
    "LESSTHAN",
    "LESSTHANEQUALS",
    "GREATERTHAN",
    "GREATERTHANEQUALS",
    "OROR",
    "ANDAND",
    "BANG",
    "ELSE",
    "IF",
    "WHILE",
    "BREAK",
    "CONTINUE"
)
t_ignore = r" "


def t_IDENT(t):
    r"[A-Za-z][A-Za-z0-9_]*"
    t.type = reserved.get(t.value, "IDENT")
    return t


t_PLUS = r"\+"
t_MINUS = r"\-"
t_TIMES = r"\*"
t_DIVIDE = r"\/"
t_MOD = r"\%"
t_AND = r"\&"
t_OR = r"\|"
t_XOR = r"\^"
t_LSHIFT = r"<<"
t_RSHIFT = r">>"
t_TILDE = r"\~"
t_LBRACE = r"{"
t_RBRACE = r"}"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_EQUALS = r"="
t_COLON = r"\:"
t_SEMICOLON = r";"
t_EQUALSEQUALS = r"=="
t_NOTEQUALS = r"!="
t_LESSTHAN = r"<"
t_LESSTHANEQUALS = r"<="
t_GREATERTHAN = r">"
t_GREATERTHANEQUALS = r">="
t_ANDAND = r"\&\&"
t_OROR = r"\|\|"
t_BANG = r"!"
t_IF = r"if"
t_ELSE = r"else"
t_WHILE = r"while"


def t_COMMENT(t):
    r"//.*"
    pass


def t_NUMBER(t):
    r"0|[1-9][0-9]*"
    t.value = int(t.value)
    return t


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


lexer = lex.lex()

if __name__ == "__main__":
    import sys

    with open(sys.argv[1]) as fp:
        source = fp.read()
    print(source)
    lexer.input(source)
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more input
        print(tok.type, tok.value, tok.lineno, tok.lexpos)

import ply.yacc as yacc

from .scanner import tokens
from .bxast import *


precedence = (
    ("left", "OROR"),
    ("left", "ANDAND"),
    ("left", "OR"),
    ("left", "XOR"),
    ("left", "AND"),
    ("nonassoc", "EQUALSEQUALS", "NOTEQUALS"),
    ("nonassoc", "LESSTHAN", "LESSTHANEQUALS", "GREATERTHAN", "GREATERTHANEQUALS"),
    ("left", "LSHIFT", "RSHIFT"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE", "MOD"),
    ("right", "TILDE"),
    ("right", "UMINUS", "BANG"),
)
def p_program(p):
    "program : declstar"
    p[0] = p[1]


def p_decl(p):
    """
    decl : function 
         | vardecl
    """
    p[0] = p[1]

def p_declstar(p):
    """
    declstar : decl
             | declstar decl
    """
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])

def p_ty(p):
    """
    ty : BOOL 
       | INT
    """
    p[0] = PrimiType(p[1])

def p_function_param(p):
    """
    function : DEF IDENT LPAREN paramlist RPAREN block
            | DEF IDENT LPAREN paramlist RPAREN COLON ty block
    """
    if len(p) > 7:
        p[0] = Function(p[2], p[6], return_ty=p[5], params=p[4])
    else:
        p[0] = Function(p[2], p[8], return_ty=VoidType(), params=p[4])

def p_function_unparam(p):
    """
    function : DEF IDENT LPAREN  RPAREN block
            | DEF IDENT LPAREN  RPAREN COLON ty block
    """
    if len(p) > 6:
        p[0] = Function(p[2], p[7], return_ty=p[5], params=[])
    else:
        p[0] = Function(p[2], p[5], return_ty=VoidType(), params=[])
def p_identlist(p):
    """
    identlist : IDENT
              | IDENT COMMA identlist
    """
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[3]
        p[0].append(p[1])

def p_param_identlist(p):
    """
    param : identlist COLON ty
    """
    p[0] = [(ident, p[3]) for ident in p[1]]

def p_param_ident(p):
    """
    param : IDENT COLON ty
    """
    p[0] = [p[1], p[3]]

def p_paramlist(p):
    """
    paramlist : param
          | param COMMA paramlist
    """
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[3]
        p[0] += p[1]

def p_block(p):
    "block : LBRACE stmts RBRACE"
    p[0] = Block(p[2])

def p_stmts(p):
    "stmts : stmtstar"
    p[0] = p[1]


def p_stmtstar(p):
    """stmtstar :
    | stmtstar stmt"""
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]
        p[0].append(p[2])


def p_vardecl(p):
    "vardecl : VAR IDENT EQUALS expr COLON ty SEMICOLON"
    p[0] = StatementDecl(p[2], p[6], p[4])

def p_stmt_vardecl(p):
    "stmt : vardecl"
    p[0] = p[1]
def p_stmt_continue(p):
    "stmt : CONTINUE SEMICOLON"
    p[0] = StatementContinue()

def p_stmt_block(p):
    "stmt :  block"
    p[0] = StatementBlock(p[1])

def p_stmt_break(p):
    "stmt : BREAK SEMICOLON"
    p[0] = StatementBreak()

def p_stmt_return(p):
    """
    stmt : RETURN expr
         | RETURN
    """
    if len(p) == 3:
        p[0] = StatementReturn(p[2])
    else:
        p[0] = StatementReturn(None)

def p_stmt_print(p):
    "stmt : PRINT LPAREN expr RPAREN SEMICOLON"
    p[0] = StatementEval(ExpressionCall("print", [p[3]]))


def p_stmt_assign(p):
    "stmt : IDENT EQUALS expr SEMICOLON"
    p[0] = StatementAssign(p[1], p[3])


def p_stmt_if_then(p):
    """
    stmt : IF LPAREN expr RPAREN block
    """
    p[0] = StatementIf(p[3], p[5], None)


def p_stmt_if_else(p):
    "stmt : IF LPAREN expr RPAREN block ELSE block"
    p[0] = StatementIf(p[3], p[5], p[7])


def p_stmt_while(p):
    "stmt : WHILE LPAREN expr RPAREN block"
    p[0] = StatementWhile(p[3], p[5])


def p_expr_number(p):
    "expr : NUMBER"
    p[0] = ExpressionInt(p[1])


def p_expr_bool(p):
    """expr : TRUE
    | FALSE
    """
    if p[1] == "true":
        p[0] = ExpressionBool(True)
    else:
        p[0] = ExpressionBool(False)


def p_expr_ident(p):
    "expr : IDENT"
    p[0] = ExpressionVar(p[1])


def p_expr_unop(p):
    """expr : TILDE expr
    | MINUS expr %prec UMINUS
    | BANG expr
    """
    if p[1] == "~":
        p[0] = ExpressionUniOp("bitwise-negation", p[2])
    elif p[1] == "!":
        p[0] = ExpressionUniOp("boolean-negation", p[2])
    else:
        p[0] = ExpressionUniOp("opposite", p[2])


def p_expr_parens(p):
    "expr : LPAREN expr RPAREN"
    p[0] = p[2]


def p_expr_binop(p):
    """expr : expr ANDAND expr
    | expr PLUS expr
    | expr OROR expr
    | expr MINUS expr
    | expr TIMES expr
    | expr DIVIDE expr
    | expr EQUALSEQUALS expr
    | expr MOD expr
    | expr XOR expr
    | expr AND expr
    | expr OR expr
    | expr LSHIFT expr
    | expr RSHIFT expr
    | expr LESSTHAN expr
    | expr GREATERTHAN expr
    | expr LESSTHANEQUALS expr
    | expr GREATERTHANEQUALS expr
    | expr NOTEQUALS expr
    """
    p[0] = ExpressionBinOp(TOKEN_TO_BINOP[p[2]], p[1], p[3])


def p_error(p):
    print(f"Syntax error in input! {p}")


parser = yacc.yacc(start="program")

TOKEN_TO_BINOP = {
    "&": "bitwise-and",
    "&&": "boolean-and",
    "|": "bitwise-or",
    "||": "boolean-or",
    "<": "lt",
    "<=": "lte",
    ">": "gt",
    ">=": "gte",
    "==": "equals",
    "!=": "notequals",
    "+": "addition",
    "-": "subtraction",
    "*": "multiplication",
    "/": "division",
    "%": "modulus",
    "^": "bitwise-xor",
    "~": "bitwise-negation",
    "!": "boolean-negation",
    "<<": "lshift",
    ">>": "rshift",
}

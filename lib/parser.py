import ply.yacc as yacc

from .scanner import tokens
from .bxast import *


precedence = (
        ('left', 'OROR'),
        ('left', 'ANDAND'),
        ('left', 'OR'),
        ('left', 'XOR'),
        ('left', 'AND'),
        ('nonassoc', 'EQUALSEQUALS', 'NOTEQUALS'),
        ('nonassoc', 'LESSTHAN', 'LESSTHANEQUALS', 'GREATERTHAN', 'GREATERTHANEQUALS'),
        ('left', 'LSHIFT', 'RSHIFT'),
        ('left' , 'PLUS', 'MINUS'),
        ('left' , 'TIMES', 'DIVIDE', 'MOD'),
        ('right', 'TILDE'),
        ('right', 'UMINUS', 'BANG'),
    )

def p_program(p):
    "program : DEF IDENT LPAREN RPAREN LBRACE stmts RBRACE"
    p[0] = Function(p[2], p[6])

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

def p_stmt_vardecl(p):
    "stmt : VAR IDENT EQUALS NUMBER COLON INT SEMICOLON"
    p[0] = StatementDecl(p[2], "int", p[4])

def p_stmt_print(p):
    "stmt : PRINT LPAREN expr RPAREN SEMICOLON"
    p[0] = StatementEval(ExpressionCall("print", [p[3]]))

def p_stmt_assign(p):
    "stmt : IDENT EQUALS expr SEMICOLON"
    p[0] = StatementAssign(p[1], p[3])

def p_expr_number(p):
    "expr : NUMBER"
    p[0] = ExpressionInt(p[1])

def p_expr_ident(p):
    "expr : IDENT"
    p[0] = ExpressionVar(p[1])

def p_expr_binop(p):
    "expr : expr binop expr"
    p[0] = ExpressionBinOp(p[2], p[1], p[3])

def p_expr_unop(p):
    """expr : TILDE expr
        | MINUS expr %prec UMINUS"""
    if p[1] == "~":
        p[0] = ExpressionUniOp("bitwise-negation", p[2])
    else:
        p[0] = ExpressionUniOp("opposite", p[2])

def p_expr_parens(p):
    "expr : LPAREN expr RPAREN"
    p[0] = p[2]

def p_unop_opp(p):
    "unop : MINUS"
    p[0] = "opposite"

def p_unop_bopp(p):
    "unop : BANG"
    p[0] = "boolean-negation"

def p_unop_neg(p):
    "unop : TILDE"
    p[0] = "bitwise-negation"

def p_binop_plus(p):
    """
    binop : PLUS
          | ANDAND
          | OROR
          | MINUS
          | TIMES
          | DIVIDE
          | MOD
          | XOR
          | AND
          | OR
          | LSHIFT
          | RSHIFT
          | LESSTHAN
          | GREATERTHAN
          | LESSTHANEQUALS
          | GREATERTHANEQUALS
          | EQUALSEQUALS
          | NOTEQUALS
    """
    p[0] = TOKEN_TO_BINOP[p[1]]

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
    ">>": "rshift"
}
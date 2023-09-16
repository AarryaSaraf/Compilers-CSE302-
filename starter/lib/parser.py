import ply.yacc as yacc

from .scanner import tokens
from .bxast import *

def p_program(p):
    "program : DEF IDENT LPAREN RPAREN LBRACE stmts RBRACE"
    p[0] = Function(p[6])

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
    "expr : unop expr"
    p[0] = ExpressionUniOp(p[1], p[2])

def p_expr_parens(p):
    "expr : LPAREN expr RPAREN"
    p[0] = p[2]

def p_unop_opp(p):
    "unop : MINUS"
    p[0] = "opposite"

def p_unop_neg(p):
    "unop : TILDE"
    p[0] = "bitwise-negation"

def p_binop_plus(p):
    "binop : PLUS"
    p[0] = "addition"

def p_binop_minus(p):
    "binop : MINUS"
    p[0] = "subtraction"

def p_binop_mul(p):
    "binop : TIMES"
    p[0] = "multiplication"

def p_binop_div(p):
    "binop : DIVIDE"
    p[0] = "division"

def p_binop_mod(p):
    "binop : MOD"
    p[0] = "modulus"

def p_binop_xor(p):
    "binop : XOR"
    p[0] = "bitwise-xor"

def p_binop_and(p):
    "binop : AND"
    p[0] = "bitwise-and"

def p_binop_or(p):
    "binop : OR"
    p[0] = "bitwise-or"

def p_binop_lshift(p):
    "binop : LSHIFT"
    p[0] = "lshift"

def p_binop_rshift(p):
    "binop : RSHIFT"
    p[0] = "rshift"
    
def p_error(p):
    print(f"Syntax error in input! {p}")

parser = yacc.yacc(start="program")


    
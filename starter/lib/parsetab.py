
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'programleftORleftXORleftANDleftLSHIFTRSHIFTleftPLUSMINUSleftTIMESDIVIDEMODrightTILDErightUMINUSAND COLON COMMENT DEF DIVIDE EQUALS IDENT INT LBRACE LPAREN LSHIFT MAIN MINUS MOD NUMBER OR PLUS PRINT RBRACE RPAREN RSHIFT SEMICOLON TILDE TIMES VAR XORprogram : DEF IDENT LPAREN RPAREN LBRACE stmts RBRACEstmts : stmtstarstmtstar : \n                | stmtstar stmtstmt : VAR IDENT EQUALS NUMBER COLON INT SEMICOLONstmt : PRINT LPAREN expr RPAREN SEMICOLONstmt : IDENT EQUALS expr SEMICOLONexpr : NUMBERexpr : IDENTexpr : expr binop exprexpr : TILDE expr\n        | MINUS expr %prec UMINUSexpr : LPAREN expr RPARENunop : MINUSunop : TILDEbinop : PLUSbinop : MINUSbinop : TIMESbinop : DIVIDEbinop : MODbinop : XORbinop : ANDbinop : ORbinop : LSHIFTbinop : RSHIFT'
    
_lr_action_items = {'DEF':([0,],[2,]),'$end':([1,9,],[0,-1,]),'IDENT':([2,6,8,10,11,15,16,21,22,23,26,27,28,29,30,31,32,33,34,35,36,37,45,47,],[3,-3,12,-4,14,18,18,18,18,18,-7,18,-16,-17,-18,-19,-20,-21,-22,-23,-24,-25,-6,-5,]),'LPAREN':([3,13,15,16,21,22,23,27,28,29,30,31,32,33,34,35,36,37,],[4,16,23,23,23,23,23,23,-16,-17,-18,-19,-20,-21,-22,-23,-24,-25,]),'RPAREN':([4,18,20,24,38,39,40,43,44,],[5,-9,-8,41,-11,-12,44,-10,-13,]),'LBRACE':([5,],[6,]),'VAR':([6,8,10,26,45,47,],[-3,11,-4,-7,-6,-5,]),'PRINT':([6,8,10,26,45,47,],[-3,13,-4,-7,-6,-5,]),'RBRACE':([6,7,8,10,26,45,47,],[-3,9,-2,-4,-7,-6,-5,]),'EQUALS':([12,14,],[15,17,]),'NUMBER':([15,16,17,21,22,23,27,28,29,30,31,32,33,34,35,36,37,],[20,20,25,20,20,20,20,-16,-17,-18,-19,-20,-21,-22,-23,-24,-25,]),'TILDE':([15,16,21,22,23,27,28,29,30,31,32,33,34,35,36,37,],[21,21,21,21,21,21,-16,-17,-18,-19,-20,-21,-22,-23,-24,-25,]),'MINUS':([15,16,18,19,20,21,22,23,24,27,28,29,30,31,32,33,34,35,36,37,38,39,40,43,44,],[22,22,-9,29,-8,22,22,22,29,22,-16,-17,-18,-19,-20,-21,-22,-23,-24,-25,-11,-12,29,29,-13,]),'SEMICOLON':([18,19,20,38,39,41,43,44,46,],[-9,26,-8,-11,-12,45,-10,-13,47,]),'PLUS':([18,19,20,24,38,39,40,43,44,],[-9,28,-8,28,-11,-12,28,28,-13,]),'TIMES':([18,19,20,24,38,39,40,43,44,],[-9,30,-8,30,-11,-12,30,30,-13,]),'DIVIDE':([18,19,20,24,38,39,40,43,44,],[-9,31,-8,31,-11,-12,31,31,-13,]),'MOD':([18,19,20,24,38,39,40,43,44,],[-9,32,-8,32,-11,-12,32,32,-13,]),'XOR':([18,19,20,24,38,39,40,43,44,],[-9,33,-8,33,-11,-12,33,33,-13,]),'AND':([18,19,20,24,38,39,40,43,44,],[-9,34,-8,34,-11,-12,34,34,-13,]),'OR':([18,19,20,24,38,39,40,43,44,],[-9,35,-8,35,-11,-12,35,35,-13,]),'LSHIFT':([18,19,20,24,38,39,40,43,44,],[-9,36,-8,36,-11,-12,36,36,-13,]),'RSHIFT':([18,19,20,24,38,39,40,43,44,],[-9,37,-8,37,-11,-12,37,37,-13,]),'COLON':([25,],[42,]),'INT':([42,],[46,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'program':([0,],[1,]),'stmts':([6,],[7,]),'stmtstar':([6,],[8,]),'stmt':([8,],[10,]),'expr':([15,16,21,22,23,27,],[19,24,38,39,40,43,]),'binop':([19,24,38,39,40,43,],[27,27,27,27,27,27,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> program","S'",1,None,None,None),
  ('program -> DEF IDENT LPAREN RPAREN LBRACE stmts RBRACE','program',7,'p_program','parser.py',19),
  ('stmts -> stmtstar','stmts',1,'p_stmts','parser.py',23),
  ('stmtstar -> <empty>','stmtstar',0,'p_stmtstar','parser.py',27),
  ('stmtstar -> stmtstar stmt','stmtstar',2,'p_stmtstar','parser.py',28),
  ('stmt -> VAR IDENT EQUALS NUMBER COLON INT SEMICOLON','stmt',7,'p_stmt_vardecl','parser.py',36),
  ('stmt -> PRINT LPAREN expr RPAREN SEMICOLON','stmt',5,'p_stmt_print','parser.py',40),
  ('stmt -> IDENT EQUALS expr SEMICOLON','stmt',4,'p_stmt_assign','parser.py',44),
  ('expr -> NUMBER','expr',1,'p_expr_number','parser.py',48),
  ('expr -> IDENT','expr',1,'p_expr_ident','parser.py',52),
  ('expr -> expr binop expr','expr',3,'p_expr_binop','parser.py',56),
  ('expr -> TILDE expr','expr',2,'p_expr_unop','parser.py',60),
  ('expr -> MINUS expr','expr',2,'p_expr_unop','parser.py',61),
  ('expr -> LPAREN expr RPAREN','expr',3,'p_expr_parens','parser.py',68),
  ('unop -> MINUS','unop',1,'p_unop_opp','parser.py',72),
  ('unop -> TILDE','unop',1,'p_unop_neg','parser.py',76),
  ('binop -> PLUS','binop',1,'p_binop_plus','parser.py',80),
  ('binop -> MINUS','binop',1,'p_binop_minus','parser.py',84),
  ('binop -> TIMES','binop',1,'p_binop_mul','parser.py',88),
  ('binop -> DIVIDE','binop',1,'p_binop_div','parser.py',92),
  ('binop -> MOD','binop',1,'p_binop_mod','parser.py',96),
  ('binop -> XOR','binop',1,'p_binop_xor','parser.py',100),
  ('binop -> AND','binop',1,'p_binop_and','parser.py',104),
  ('binop -> OR','binop',1,'p_binop_or','parser.py',108),
  ('binop -> LSHIFT','binop',1,'p_binop_lshift','parser.py',112),
  ('binop -> RSHIFT','binop',1,'p_binop_rshift','parser.py',116),
]

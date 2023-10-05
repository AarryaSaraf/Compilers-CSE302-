
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'programleftORORleftANDANDleftORleftXORleftANDnonassocEQUALSEQUALSNOTEQUALSnonassocLESSTHANLESSTHANEQUALSGREATERTHANGREATERTHANEQUALSleftLSHIFTRSHIFTleftPLUSMINUSleftTIMESDIVIDEMODrightTILDErightUMINUSBANGAND ANDAND BANG COLON COMMENT DEF DIVIDE ELSE EQUALS EQUALSEQUALS GREATERTHAN GREATERTHANEQUALS IDENT IF INT LBRACE LESSTHAN LESSTHANEQUALS LPAREN LSHIFT MAIN MINUS MOD NOTEQUALS NUMBER OR OROR PLUS PRINT RBRACE RPAREN RSHIFT SEMICOLON TILDE TIMES VAR WHILE XORprogram : DEF IDENT LPAREN RPAREN blockblock : LBRACE stmts RBRACEstmts : stmtstarstmtstar :\n    | stmtstar stmtstmt : VAR IDENT EQUALS NUMBER COLON INT SEMICOLONstmt : PRINT LPAREN expr RPAREN SEMICOLONstmt : IDENT EQUALS expr SEMICOLON\n    stmt : IF LPAREN expr RPAREN block\n         | IF LPAREN expr RPAREN block ELSE block\n    stmt : WHILE LPAREN expr RPAREN blockexpr : NUMBERexpr : IDENTexpr : expr binop exprexpr : TILDE expr\n    | MINUS expr %prec UMINUSexpr : LPAREN expr RPARENunop : MINUSunop : BANGunop : TILDE\n    binop : PLUS\n          | ANDAND\n          | OROR\n          | MINUS\n          | TIMES\n          | DIVIDE\n          | MOD\n          | XOR\n          | AND\n          | OR\n          | LSHIFT\n          | RSHIFT\n          | LESSTHAN\n          | GREATERTHAN\n          | LESSTHANEQUALS\n          | GREATERTHANEQUALS\n          | EQUALSEQUALS\n          | NOTEQUALS\n    '
    
_lr_action_items = {'DEF':([0,],[2,]),'$end':([1,6,10,],[0,-1,-2,]),'IDENT':([2,7,9,10,11,12,18,19,20,21,26,27,28,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,62,63,64,67,68,],[3,-4,13,-2,-5,17,23,23,23,23,23,23,23,-8,23,-21,-22,-23,-24,-25,-26,-27,-28,-29,-30,-31,-32,-33,-34,-35,-36,-37,-38,-7,-9,-11,-6,-10,]),'LPAREN':([3,14,15,16,18,19,20,21,26,27,28,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,],[4,19,20,21,28,28,28,28,28,28,28,28,-21,-22,-23,-24,-25,-26,-27,-28,-29,-30,-31,-32,-33,-34,-35,-36,-37,-38,]),'RPAREN':([4,23,25,29,30,31,53,54,55,60,61,],[5,-13,-12,56,57,58,-15,-16,61,-14,-17,]),'LBRACE':([5,57,58,66,],[7,7,7,7,]),'VAR':([7,9,10,11,33,62,63,64,67,68,],[-4,12,-2,-5,-8,-7,-9,-11,-6,-10,]),'PRINT':([7,9,10,11,33,62,63,64,67,68,],[-4,14,-2,-5,-8,-7,-9,-11,-6,-10,]),'IF':([7,9,10,11,33,62,63,64,67,68,],[-4,15,-2,-5,-8,-7,-9,-11,-6,-10,]),'WHILE':([7,9,10,11,33,62,63,64,67,68,],[-4,16,-2,-5,-8,-7,-9,-11,-6,-10,]),'RBRACE':([7,8,9,10,11,33,62,63,64,67,68,],[-4,10,-3,-2,-5,-8,-7,-9,-11,-6,-10,]),'ELSE':([10,63,],[-2,66,]),'EQUALS':([13,17,],[18,22,]),'NUMBER':([18,19,20,21,22,26,27,28,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,],[25,25,25,25,32,25,25,25,25,-21,-22,-23,-24,-25,-26,-27,-28,-29,-30,-31,-32,-33,-34,-35,-36,-37,-38,]),'TILDE':([18,19,20,21,26,27,28,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,],[26,26,26,26,26,26,26,26,-21,-22,-23,-24,-25,-26,-27,-28,-29,-30,-31,-32,-33,-34,-35,-36,-37,-38,]),'MINUS':([18,19,20,21,23,24,25,26,27,28,29,30,31,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,60,61,],[27,27,27,27,-13,38,-12,27,27,27,38,38,38,27,-21,-22,-23,-24,-25,-26,-27,-28,-29,-30,-31,-32,-33,-34,-35,-36,-37,-38,-15,-16,38,38,-17,]),'SEMICOLON':([23,24,25,53,54,56,60,61,65,],[-13,33,-12,-15,-16,62,-14,-17,67,]),'PLUS':([23,24,25,29,30,31,53,54,55,60,61,],[-13,35,-12,35,35,35,-15,-16,35,35,-17,]),'ANDAND':([23,24,25,29,30,31,53,54,55,60,61,],[-13,36,-12,36,36,36,-15,-16,36,36,-17,]),'OROR':([23,24,25,29,30,31,53,54,55,60,61,],[-13,37,-12,37,37,37,-15,-16,37,37,-17,]),'TIMES':([23,24,25,29,30,31,53,54,55,60,61,],[-13,39,-12,39,39,39,-15,-16,39,39,-17,]),'DIVIDE':([23,24,25,29,30,31,53,54,55,60,61,],[-13,40,-12,40,40,40,-15,-16,40,40,-17,]),'MOD':([23,24,25,29,30,31,53,54,55,60,61,],[-13,41,-12,41,41,41,-15,-16,41,41,-17,]),'XOR':([23,24,25,29,30,31,53,54,55,60,61,],[-13,42,-12,42,42,42,-15,-16,42,42,-17,]),'AND':([23,24,25,29,30,31,53,54,55,60,61,],[-13,43,-12,43,43,43,-15,-16,43,43,-17,]),'OR':([23,24,25,29,30,31,53,54,55,60,61,],[-13,44,-12,44,44,44,-15,-16,44,44,-17,]),'LSHIFT':([23,24,25,29,30,31,53,54,55,60,61,],[-13,45,-12,45,45,45,-15,-16,45,45,-17,]),'RSHIFT':([23,24,25,29,30,31,53,54,55,60,61,],[-13,46,-12,46,46,46,-15,-16,46,46,-17,]),'LESSTHAN':([23,24,25,29,30,31,53,54,55,60,61,],[-13,47,-12,47,47,47,-15,-16,47,47,-17,]),'GREATERTHAN':([23,24,25,29,30,31,53,54,55,60,61,],[-13,48,-12,48,48,48,-15,-16,48,48,-17,]),'LESSTHANEQUALS':([23,24,25,29,30,31,53,54,55,60,61,],[-13,49,-12,49,49,49,-15,-16,49,49,-17,]),'GREATERTHANEQUALS':([23,24,25,29,30,31,53,54,55,60,61,],[-13,50,-12,50,50,50,-15,-16,50,50,-17,]),'EQUALSEQUALS':([23,24,25,29,30,31,53,54,55,60,61,],[-13,51,-12,51,51,51,-15,-16,51,51,-17,]),'NOTEQUALS':([23,24,25,29,30,31,53,54,55,60,61,],[-13,52,-12,52,52,52,-15,-16,52,52,-17,]),'COLON':([32,],[59,]),'INT':([59,],[65,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'program':([0,],[1,]),'block':([5,57,58,66,],[6,63,64,68,]),'stmts':([7,],[8,]),'stmtstar':([7,],[9,]),'stmt':([9,],[11,]),'expr':([18,19,20,21,26,27,28,34,],[24,29,30,31,53,54,55,60,]),'binop':([24,29,30,31,53,54,55,60,],[34,34,34,34,34,34,34,34,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> program","S'",1,None,None,None),
  ('program -> DEF IDENT LPAREN RPAREN block','program',5,'p_program','parser.py',24),
  ('block -> LBRACE stmts RBRACE','block',3,'p_block','parser.py',29),
  ('stmts -> stmtstar','stmts',1,'p_stmts','parser.py',34),
  ('stmtstar -> <empty>','stmtstar',0,'p_stmtstar','parser.py',39),
  ('stmtstar -> stmtstar stmt','stmtstar',2,'p_stmtstar','parser.py',40),
  ('stmt -> VAR IDENT EQUALS NUMBER COLON INT SEMICOLON','stmt',7,'p_stmt_vardecl','parser.py',49),
  ('stmt -> PRINT LPAREN expr RPAREN SEMICOLON','stmt',5,'p_stmt_print','parser.py',54),
  ('stmt -> IDENT EQUALS expr SEMICOLON','stmt',4,'p_stmt_assign','parser.py',59),
  ('stmt -> IF LPAREN expr RPAREN block','stmt',5,'p_stmt_if','parser.py',65),
  ('stmt -> IF LPAREN expr RPAREN block ELSE block','stmt',7,'p_stmt_if','parser.py',66),
  ('stmt -> WHILE LPAREN expr RPAREN block','stmt',5,'p_stmt_while','parser.py',75),
  ('expr -> NUMBER','expr',1,'p_expr_number','parser.py',80),
  ('expr -> IDENT','expr',1,'p_expr_ident','parser.py',85),
  ('expr -> expr binop expr','expr',3,'p_expr_binop','parser.py',90),
  ('expr -> TILDE expr','expr',2,'p_expr_unop','parser.py',95),
  ('expr -> MINUS expr','expr',2,'p_expr_unop','parser.py',96),
  ('expr -> LPAREN expr RPAREN','expr',3,'p_expr_parens','parser.py',104),
  ('unop -> MINUS','unop',1,'p_unop_opp','parser.py',109),
  ('unop -> BANG','unop',1,'p_unop_bopp','parser.py',114),
  ('unop -> TILDE','unop',1,'p_unop_neg','parser.py',119),
  ('binop -> PLUS','binop',1,'p_binop_plus','parser.py',125),
  ('binop -> ANDAND','binop',1,'p_binop_plus','parser.py',126),
  ('binop -> OROR','binop',1,'p_binop_plus','parser.py',127),
  ('binop -> MINUS','binop',1,'p_binop_plus','parser.py',128),
  ('binop -> TIMES','binop',1,'p_binop_plus','parser.py',129),
  ('binop -> DIVIDE','binop',1,'p_binop_plus','parser.py',130),
  ('binop -> MOD','binop',1,'p_binop_plus','parser.py',131),
  ('binop -> XOR','binop',1,'p_binop_plus','parser.py',132),
  ('binop -> AND','binop',1,'p_binop_plus','parser.py',133),
  ('binop -> OR','binop',1,'p_binop_plus','parser.py',134),
  ('binop -> LSHIFT','binop',1,'p_binop_plus','parser.py',135),
  ('binop -> RSHIFT','binop',1,'p_binop_plus','parser.py',136),
  ('binop -> LESSTHAN','binop',1,'p_binop_plus','parser.py',137),
  ('binop -> GREATERTHAN','binop',1,'p_binop_plus','parser.py',138),
  ('binop -> LESSTHANEQUALS','binop',1,'p_binop_plus','parser.py',139),
  ('binop -> GREATERTHANEQUALS','binop',1,'p_binop_plus','parser.py',140),
  ('binop -> EQUALSEQUALS','binop',1,'p_binop_plus','parser.py',141),
  ('binop -> NOTEQUALS','binop',1,'p_binop_plus','parser.py',142),
]

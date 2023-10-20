
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'programleftORORleftANDANDleftORleftXORleftANDnonassocEQUALSEQUALSNOTEQUALSnonassocLESSTHANLESSTHANEQUALSGREATERTHANGREATERTHANEQUALSleftLSHIFTRSHIFTleftPLUSMINUSleftTIMESDIVIDEMODrightTILDErightUMINUSBANGAND ANDAND BANG BOOL BREAK COLON COMMA COMMENT CONTINUE DEF DIVIDE ELSE EQUALS EQUALSEQUALS FALSE GREATERTHAN GREATERTHANEQUALS IDENT IF INT LBRACE LESSTHAN LESSTHANEQUALS LPAREN LSHIFT MAIN MINUS MOD NOTEQUALS NUMBER OR OROR PLUS RBRACE RETURN RPAREN RSHIFT SEMICOLON TILDE TIMES TRUE VAR WHILE XORprogram : declstar\n    decl : function\n         | vardecl\n    \n    declstar : decl\n             | declstar decl\n    \n    ty : BOOL\n       | INT\n    \n    function : DEF IDENT LPAREN paramlist RPAREN block\n            | DEF IDENT LPAREN paramlist RPAREN COLON ty block\n    \n    function : DEF IDENT LPAREN  RPAREN block\n            | DEF IDENT LPAREN  RPAREN COLON ty block\n    \n    identlist : IDENT\n              | IDENT COMMA identlist\n    \n    param : identlist COLON ty\n    \n    param : IDENT COLON ty\n    \n    paramlist : param\n          | param COMMA paramlist\n    block : LBRACE stmts RBRACEstmts : stmtstarstmtstar :\n    | stmtstar stmtvardecl : VAR IDENT EQUALS expr COLON ty SEMICOLONstmt : vardeclstmt : CONTINUE SEMICOLONstmt :  blockstmt : BREAK SEMICOLON\n    stmt : RETURN expr SEMICOLON\n         | RETURN SEMICOLON\n    stmt : call SEMICOLONstmt : IDENT EQUALS expr SEMICOLONcall : IDENT LPAREN arglist RPAREN\n    | IDENT LPAREN RPARENexpr : call\n    arglist : expr\n          | expr COMMA arglist\n    \n    stmt : IF LPAREN expr RPAREN block\n    stmt : IF LPAREN expr RPAREN block ELSE blockstmt : WHILE LPAREN expr RPAREN blockexpr : NUMBERexpr : TRUE\n    | FALSE\n    expr : IDENTexpr : TILDE expr\n    | MINUS expr %prec UMINUS\n    | BANG expr\n    expr : LPAREN expr RPARENexpr : expr ANDAND expr\n    | expr PLUS expr\n    | expr OROR expr\n    | expr MINUS expr\n    | expr TIMES expr\n    | expr DIVIDE expr\n    | expr EQUALSEQUALS expr\n    | expr MOD expr\n    | expr XOR expr\n    | expr AND expr\n    | expr OR expr\n    | expr LSHIFT expr\n    | expr RSHIFT expr\n    | expr LESSTHAN expr\n    | expr GREATERTHAN expr\n    | expr LESSTHANEQUALS expr\n    | expr GREATERTHANEQUALS expr\n    | expr NOTEQUALS expr\n    '
    
_lr_action_items = {'DEF':([0,2,3,4,5,8,31,65,96,97,110,111,],[6,6,-4,-2,-3,-5,-10,-8,-11,-18,-22,-9,]),'VAR':([0,2,3,4,5,8,31,33,65,69,96,97,98,99,101,110,111,112,113,115,116,121,125,128,129,131,],[7,7,-4,-2,-3,-5,-10,-20,-8,7,-11,-18,-21,-23,-25,-22,-9,-24,-26,-28,-29,-27,-30,-36,-38,-37,]),'$end':([1,2,3,4,5,8,31,65,96,97,110,111,],[0,-1,-4,-2,-3,-5,-10,-8,-11,-18,-22,-9,]),'IDENT':([6,7,11,12,24,25,26,27,29,33,34,36,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,69,97,98,99,101,103,109,110,112,113,115,116,117,118,119,121,125,128,129,131,],[9,10,13,18,18,18,18,18,63,-20,13,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,105,-18,-21,-23,-25,18,18,-22,-24,-26,-28,-29,18,18,18,-27,-30,-36,-38,-37,]),'LPAREN':([9,12,18,24,25,26,27,36,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,103,105,106,107,109,117,118,119,],[11,27,36,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,36,118,119,27,27,27,27,]),'EQUALS':([10,105,],[12,117,]),'RPAREN':([11,14,16,18,20,21,22,23,36,56,57,58,59,60,61,62,70,71,72,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,120,123,124,],[15,30,-16,-42,-33,-39,-40,-41,73,-43,-44,-45,94,-15,-6,-7,-17,-14,108,-32,-34,-47,-48,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,-60,-61,-62,-63,-64,-46,-31,-35,126,127,]),'NUMBER':([12,24,25,26,27,36,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,103,109,117,118,119,],[21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,]),'TRUE':([12,24,25,26,27,36,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,103,109,117,118,119,],[22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,]),'FALSE':([12,24,25,26,27,36,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,103,109,117,118,119,],[23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,]),'TILDE':([12,24,25,26,27,36,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,103,109,117,118,119,],[24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,]),'MINUS':([12,18,19,20,21,22,23,24,25,26,27,36,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,103,108,109,114,117,118,119,122,123,124,],[25,-42,41,-33,-39,-40,-41,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,-43,-44,-45,41,-32,41,41,-48,41,-50,-51,-52,41,-54,41,41,41,41,41,41,41,41,41,41,-46,25,-31,25,41,25,25,25,41,41,41,]),'BANG':([12,24,25,26,27,36,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,103,109,117,118,119,],[26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,]),'COLON':([13,15,17,18,19,20,21,22,23,30,56,57,58,63,64,73,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,],[28,32,35,-42,37,-33,-39,-40,-41,66,-43,-44,-45,-12,-13,-32,-47,-48,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,-60,-61,-62,-63,-64,-46,-31,]),'COMMA':([13,16,18,20,21,22,23,56,57,58,60,61,62,63,71,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,],[29,34,-42,-33,-39,-40,-41,-43,-44,-45,-15,-6,-7,29,-14,-32,109,-47,-48,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,-60,-61,-62,-63,-64,-46,-31,]),'LBRACE':([15,30,33,61,62,67,69,95,97,98,99,101,110,112,113,115,116,121,125,126,127,128,129,130,131,],[33,33,-20,-6,-7,33,33,33,-18,-21,-23,-25,-22,-24,-26,-28,-29,-27,-30,33,33,-36,-38,33,-37,]),'ANDAND':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,38,-33,-39,-40,-41,-43,-44,-45,38,-32,38,-47,-48,38,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,-60,-61,-62,-63,-64,-46,-31,38,38,38,38,]),'PLUS':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,39,-33,-39,-40,-41,-43,-44,-45,39,-32,39,39,-48,39,-50,-51,-52,39,-54,39,39,39,39,39,39,39,39,39,39,-46,-31,39,39,39,39,]),'OROR':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,40,-33,-39,-40,-41,-43,-44,-45,40,-32,40,-47,-48,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,-60,-61,-62,-63,-64,-46,-31,40,40,40,40,]),'TIMES':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,42,-33,-39,-40,-41,-43,-44,-45,42,-32,42,42,42,42,42,-51,-52,42,-54,42,42,42,42,42,42,42,42,42,42,-46,-31,42,42,42,42,]),'DIVIDE':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,43,-33,-39,-40,-41,-43,-44,-45,43,-32,43,43,43,43,43,-51,-52,43,-54,43,43,43,43,43,43,43,43,43,43,-46,-31,43,43,43,43,]),'EQUALSEQUALS':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,44,-33,-39,-40,-41,-43,-44,-45,44,-32,44,44,-48,44,-50,-51,-52,None,-54,44,44,44,-58,-59,-60,-61,-62,-63,None,-46,-31,44,44,44,44,]),'MOD':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,45,-33,-39,-40,-41,-43,-44,-45,45,-32,45,45,45,45,45,-51,-52,45,-54,45,45,45,45,45,45,45,45,45,45,-46,-31,45,45,45,45,]),'XOR':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,46,-33,-39,-40,-41,-43,-44,-45,46,-32,46,46,-48,46,-50,-51,-52,-53,-54,-55,-56,46,-58,-59,-60,-61,-62,-63,-64,-46,-31,46,46,46,46,]),'AND':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,47,-33,-39,-40,-41,-43,-44,-45,47,-32,47,47,-48,47,-50,-51,-52,-53,-54,47,-56,47,-58,-59,-60,-61,-62,-63,-64,-46,-31,47,47,47,47,]),'OR':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,48,-33,-39,-40,-41,-43,-44,-45,48,-32,48,48,-48,48,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,-60,-61,-62,-63,-64,-46,-31,48,48,48,48,]),'LSHIFT':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,49,-33,-39,-40,-41,-43,-44,-45,49,-32,49,49,-48,49,-50,-51,-52,49,-54,49,49,49,-58,-59,49,49,49,49,49,-46,-31,49,49,49,49,]),'RSHIFT':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,50,-33,-39,-40,-41,-43,-44,-45,50,-32,50,50,-48,50,-50,-51,-52,50,-54,50,50,50,-58,-59,50,50,50,50,50,-46,-31,50,50,50,50,]),'LESSTHAN':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,51,-33,-39,-40,-41,-43,-44,-45,51,-32,51,51,-48,51,-50,-51,-52,51,-54,51,51,51,-58,-59,None,None,None,None,51,-46,-31,51,51,51,51,]),'GREATERTHAN':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,52,-33,-39,-40,-41,-43,-44,-45,52,-32,52,52,-48,52,-50,-51,-52,52,-54,52,52,52,-58,-59,None,None,None,None,52,-46,-31,52,52,52,52,]),'LESSTHANEQUALS':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,53,-33,-39,-40,-41,-43,-44,-45,53,-32,53,53,-48,53,-50,-51,-52,53,-54,53,53,53,-58,-59,None,None,None,None,53,-46,-31,53,53,53,53,]),'GREATERTHANEQUALS':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,54,-33,-39,-40,-41,-43,-44,-45,54,-32,54,54,-48,54,-50,-51,-52,54,-54,54,54,54,-58,-59,None,None,None,None,54,-46,-31,54,54,54,54,]),'NOTEQUALS':([18,19,20,21,22,23,56,57,58,59,73,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,108,114,122,123,124,],[-42,55,-33,-39,-40,-41,-43,-44,-45,55,-32,55,55,-48,55,-50,-51,-52,None,-54,55,55,55,-58,-59,-60,-61,-62,-63,None,-46,-31,55,55,55,55,]),'SEMICOLON':([18,20,21,22,23,56,57,58,61,62,73,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,100,102,103,104,108,114,122,],[-42,-33,-39,-40,-41,-43,-44,-45,-6,-7,-32,110,-47,-48,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,-60,-61,-62,-63,-64,-46,112,113,115,116,-31,121,125,]),'BOOL':([28,32,35,37,66,],[61,61,61,61,61,]),'INT':([28,32,35,37,66,],[62,62,62,62,62,]),'CONTINUE':([33,69,97,98,99,101,110,112,113,115,116,121,125,128,129,131,],[-20,100,-18,-21,-23,-25,-22,-24,-26,-28,-29,-27,-30,-36,-38,-37,]),'BREAK':([33,69,97,98,99,101,110,112,113,115,116,121,125,128,129,131,],[-20,102,-18,-21,-23,-25,-22,-24,-26,-28,-29,-27,-30,-36,-38,-37,]),'RETURN':([33,69,97,98,99,101,110,112,113,115,116,121,125,128,129,131,],[-20,103,-18,-21,-23,-25,-22,-24,-26,-28,-29,-27,-30,-36,-38,-37,]),'IF':([33,69,97,98,99,101,110,112,113,115,116,121,125,128,129,131,],[-20,106,-18,-21,-23,-25,-22,-24,-26,-28,-29,-27,-30,-36,-38,-37,]),'WHILE':([33,69,97,98,99,101,110,112,113,115,116,121,125,128,129,131,],[-20,107,-18,-21,-23,-25,-22,-24,-26,-28,-29,-27,-30,-36,-38,-37,]),'RBRACE':([33,68,69,97,98,99,101,110,112,113,115,116,121,125,128,129,131,],[-20,97,-19,-18,-21,-23,-25,-22,-24,-26,-28,-29,-27,-30,-36,-38,-37,]),'ELSE':([97,128,],[-18,130,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'program':([0,],[1,]),'declstar':([0,],[2,]),'decl':([0,2,],[3,8,]),'function':([0,2,],[4,4,]),'vardecl':([0,2,69,],[5,5,99,]),'paramlist':([11,34,],[14,70,]),'param':([11,34,],[16,16,]),'identlist':([11,29,34,],[17,64,17,]),'expr':([12,24,25,26,27,36,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,103,109,117,118,119,],[19,56,57,58,59,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,114,74,122,123,124,]),'call':([12,24,25,26,27,36,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,69,103,109,117,118,119,],[20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,104,20,20,20,20,20,]),'block':([15,30,67,69,95,126,127,130,],[31,65,96,101,111,128,129,131,]),'ty':([28,32,35,37,66,],[60,67,71,75,95,]),'stmts':([33,],[68,]),'stmtstar':([33,],[69,]),'arglist':([36,109,],[72,120,]),'stmt':([69,],[98,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> program","S'",1,None,None,None),
  ('program -> declstar','program',1,'p_program','parser.py',24),
  ('decl -> function','decl',1,'p_decl','parser.py',30),
  ('decl -> vardecl','decl',1,'p_decl','parser.py',31),
  ('declstar -> decl','declstar',1,'p_declstar','parser.py',38),
  ('declstar -> declstar decl','declstar',2,'p_declstar','parser.py',39),
  ('ty -> BOOL','ty',1,'p_ty','parser.py',52),
  ('ty -> INT','ty',1,'p_ty','parser.py',53),
  ('function -> DEF IDENT LPAREN paramlist RPAREN block','function',6,'p_function_param','parser.py',60),
  ('function -> DEF IDENT LPAREN paramlist RPAREN COLON ty block','function',8,'p_function_param','parser.py',61),
  ('function -> DEF IDENT LPAREN RPAREN block','function',5,'p_function_unparam','parser.py',71),
  ('function -> DEF IDENT LPAREN RPAREN COLON ty block','function',7,'p_function_unparam','parser.py',72),
  ('identlist -> IDENT','identlist',1,'p_identlist','parser.py',82),
  ('identlist -> IDENT COMMA identlist','identlist',3,'p_identlist','parser.py',83),
  ('param -> identlist COLON ty','param',3,'p_param_identlist','parser.py',94),
  ('param -> IDENT COLON ty','param',3,'p_param_ident','parser.py',101),
  ('paramlist -> param','paramlist',1,'p_paramlist','parser.py',108),
  ('paramlist -> param COMMA paramlist','paramlist',3,'p_paramlist','parser.py',109),
  ('block -> LBRACE stmts RBRACE','block',3,'p_block','parser.py',121),
  ('stmts -> stmtstar','stmts',1,'p_stmts','parser.py',126),
  ('stmtstar -> <empty>','stmtstar',0,'p_stmtstar','parser.py',131),
  ('stmtstar -> stmtstar stmt','stmtstar',2,'p_stmtstar','parser.py',132),
  ('vardecl -> VAR IDENT EQUALS expr COLON ty SEMICOLON','vardecl',7,'p_vardecl','parser.py',141),
  ('stmt -> vardecl','stmt',1,'p_stmt_vardecl','parser.py',146),
  ('stmt -> CONTINUE SEMICOLON','stmt',2,'p_stmt_continue','parser.py',151),
  ('stmt -> block','stmt',1,'p_stmt_block','parser.py',156),
  ('stmt -> BREAK SEMICOLON','stmt',2,'p_stmt_break','parser.py',161),
  ('stmt -> RETURN expr SEMICOLON','stmt',3,'p_stmt_return','parser.py',167),
  ('stmt -> RETURN SEMICOLON','stmt',2,'p_stmt_return','parser.py',168),
  ('stmt -> call SEMICOLON','stmt',2,'p_stmt_eval','parser.py',177),
  ('stmt -> IDENT EQUALS expr SEMICOLON','stmt',4,'p_stmt_assign','parser.py',182),
  ('call -> IDENT LPAREN arglist RPAREN','call',4,'p_call','parser.py',187),
  ('call -> IDENT LPAREN RPAREN','call',3,'p_call','parser.py',188),
  ('expr -> call','expr',1,'p_expr_call','parser.py',196),
  ('arglist -> expr','arglist',1,'p_arglist','parser.py',202),
  ('arglist -> expr COMMA arglist','arglist',3,'p_arglist','parser.py',203),
  ('stmt -> IF LPAREN expr RPAREN block','stmt',5,'p_stmt_if_then','parser.py',216),
  ('stmt -> IF LPAREN expr RPAREN block ELSE block','stmt',7,'p_stmt_if_else','parser.py',222),
  ('stmt -> WHILE LPAREN expr RPAREN block','stmt',5,'p_stmt_while','parser.py',227),
  ('expr -> NUMBER','expr',1,'p_expr_number','parser.py',232),
  ('expr -> TRUE','expr',1,'p_expr_bool','parser.py',237),
  ('expr -> FALSE','expr',1,'p_expr_bool','parser.py',238),
  ('expr -> IDENT','expr',1,'p_expr_ident','parser.py',247),
  ('expr -> TILDE expr','expr',2,'p_expr_unop','parser.py',252),
  ('expr -> MINUS expr','expr',2,'p_expr_unop','parser.py',253),
  ('expr -> BANG expr','expr',2,'p_expr_unop','parser.py',254),
  ('expr -> LPAREN expr RPAREN','expr',3,'p_expr_parens','parser.py',265),
  ('expr -> expr ANDAND expr','expr',3,'p_expr_binop','parser.py',270),
  ('expr -> expr PLUS expr','expr',3,'p_expr_binop','parser.py',271),
  ('expr -> expr OROR expr','expr',3,'p_expr_binop','parser.py',272),
  ('expr -> expr MINUS expr','expr',3,'p_expr_binop','parser.py',273),
  ('expr -> expr TIMES expr','expr',3,'p_expr_binop','parser.py',274),
  ('expr -> expr DIVIDE expr','expr',3,'p_expr_binop','parser.py',275),
  ('expr -> expr EQUALSEQUALS expr','expr',3,'p_expr_binop','parser.py',276),
  ('expr -> expr MOD expr','expr',3,'p_expr_binop','parser.py',277),
  ('expr -> expr XOR expr','expr',3,'p_expr_binop','parser.py',278),
  ('expr -> expr AND expr','expr',3,'p_expr_binop','parser.py',279),
  ('expr -> expr OR expr','expr',3,'p_expr_binop','parser.py',280),
  ('expr -> expr LSHIFT expr','expr',3,'p_expr_binop','parser.py',281),
  ('expr -> expr RSHIFT expr','expr',3,'p_expr_binop','parser.py',282),
  ('expr -> expr LESSTHAN expr','expr',3,'p_expr_binop','parser.py',283),
  ('expr -> expr GREATERTHAN expr','expr',3,'p_expr_binop','parser.py',284),
  ('expr -> expr LESSTHANEQUALS expr','expr',3,'p_expr_binop','parser.py',285),
  ('expr -> expr GREATERTHANEQUALS expr','expr',3,'p_expr_binop','parser.py',286),
  ('expr -> expr NOTEQUALS expr','expr',3,'p_expr_binop','parser.py',287),
]

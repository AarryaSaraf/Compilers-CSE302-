from dataclasses import dataclass
from typing import List
# TODO: Add position info for error message
@dataclass
class Expression:
    pass

@dataclass
class ExpressionVar(Expression):
    name: str

@dataclass 
class ExpressionInt(Expression):
    value: int

@dataclass
class ExpressionUniOp(Expression):
    operator: str
    argument: Expression

@dataclass
class ExpressionBinOp(Expression):
    operator: str
    left: Expression
    right: Expression


@dataclass
class ExpressionCall(Expression):
    target: str
    arguments: List[Expression]

@dataclass 
class Statement:
    pass

@dataclass
class StatementDecl(Statement):
    name: str
    type: str
    init: Expression

@dataclass
class StatementAssign(Statement):
    lvalue: str # TODO refactor for general grammar later
    rvalue: Expression


@dataclass
class StatementEval(Statement):
    expr: Expression

def json_to_vardecl(json_load):
    pass

def from_json(json_load):
    match json_load[1]:
        case "<statement:vardecl>": return json_to_vardecl(json_load[2])
        case 
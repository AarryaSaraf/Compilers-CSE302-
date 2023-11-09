from dataclasses import dataclass
from typing import List, Tuple
from abc import abstractmethod
from .bxtypes import *

# TODO: Add position info for error message


@dataclass
class Expression:
    pass


@dataclass
class ExpressionVar(Expression):
    name: str
    ty: Type | None = None

    def __str__(self):
        return self.name


@dataclass
class ExpressionInt(Expression):
    value: int
    ty: Type | None = None

    def __str__(self):
        return str(self.value)


@dataclass
class ExpressionBool(Expression):
    value: bool
    ty: Type | None = None

    def __str__(self):
        return str(self.value)


@dataclass
class ExpressionUniOp(Expression):
    operator: str
    argument: Expression
    ty: Type | None = None

    def __str__(self):
        return f"({self.operator} {self.argument})"


@dataclass
class ExpressionBinOp(Expression):
    operator: str
    left: Expression
    right: Expression
    ty: Type | None = None

    def __str__(self):
        return f"({self.operator} {self.left} {self.right})"


@dataclass
class ExpressionCall(Expression):
    target: str
    arguments: List[Expression]
    ty: Type | None = None

    def __str__(self):
        return f"{self.target}({self.arguments[0]})"


@dataclass
class Statement:
    @abstractmethod
    def type_check(self):
        pass


@dataclass
class Block:
    stmts: List[Statement]


@dataclass
class StatementDecl(Statement):
    name: str
    ty: PrimiType
    init: Expression


@dataclass
class StatementBreak(Statement):
    pass


@dataclass
class StatementContinue(Statement):
    pass


@dataclass
class StatementAssign(Statement):
    lvalue: str  # TODO refactor for general grammar later
    rvalue: Expression


@dataclass
class StatementEval(Statement):
    expr: Expression


@dataclass
class StatementBlock(Statement):
    block: Block


@dataclass
class StatementIf(Statement):
    cond: Expression
    body: Block
    elseblock: None | Block


@dataclass
class StatementWhile(Statement):
    cond: Expression
    body: Block


@dataclass
class StatementReturn(Statement):
    var: Expression | None


@dataclass
class Function:
    name: str
    body: Block
    return_ty: Type
    params: List[Tuple[str, Type]]
    ty: FunctionType

    def __init__(self, name, body, return_ty, params):
        self.name = name
        self.body = body
        self.return_ty = return_ty
        self.params = params
        self.ty = FunctionType([p[1] for p in params], return_ty)


def get_name(json):
    return json[1]["value"]


# deserializing statements
def json_to_vardecl(js) -> Statement:
    return StatementDecl(get_name(js["name"]), "int", ExpressionInt(0))


def json_to_assign(js) -> Statement:
    return StatementAssign(
        lvalue=get_name(js["lvalue"][1]["name"]), rvalue=json_to_expr(js["rvalue"])
    )


def json_to_eval(js) -> Statement:
    return StatementEval(expr=json_to_expr(js["expression"]))


def json_to_statement(js) -> Statement:
    match js[0]:
        case "<statement:vardecl>":
            return json_to_vardecl(js[1])
        case "<statement:assign>":
            return json_to_assign(js[1])
        case "<statement:eval>":
            return json_to_eval(js[1])


# Expressions
def json_to_var(js) -> Expression:
    return ExpressionVar(get_name(js["name"]))


def json_to_int(js) -> Expression:
    return ExpressionInt(js["value"])


def json_to_uniop(js) -> Expression:
    return ExpressionUniOp(
        operator=get_name(js["operator"]), argument=json_to_expr(js["argument"])
    )


def json_to_binop(js) -> Expression:
    return ExpressionBinOp(
        operator=get_name(js["operator"]),
        left=json_to_expr(js["left"]),
        right=json_to_expr(js["right"]),
    )


def json_to_call(js) -> Expression:
    return ExpressionCall(
        target=get_name(js["target"]),
        arguments=[json_to_expr(expr) for expr in js["arguments"]],
    )


def json_to_expr(js) -> Expression:
    match js[0]:
        case "<expression:var>":
            return json_to_var(js[1])
        case "<expression:int>":
            return json_to_int(js[1])
        case "<expression:uniop>":
            return json_to_uniop(js[1])
        case "<expression:binop>":
            return json_to_binop(js[1])
        case "<expression:call>":
            return json_to_call(js[1])


def deserialize(js) -> List[Statement]:
    statements = js["ast"][0][1]["body"]
    return [json_to_statement(stmt) for stmt in statements]

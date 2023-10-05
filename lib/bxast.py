from dataclasses import dataclass
from typing import List
from abc import abstractmethod

# TODO: Add position info for error message
class TypeCheckError(Exception):
    def __init__(self, expr, ty, expected_ty):
        self.expr = expr
        self.ty = ty
        self.expected_ty = ty


@dataclass
class Expression:

    @abstractmethod
    def type_check(self):
        pass

@dataclass
class ExpressionVar(Expression):
    name: str
    ty: str | None = None

    def type_check(self):
        self.ty = "int"


@dataclass
class ExpressionInt(Expression):
    value: int
    ty: str | None = None

    def type_check(self):
        self.ty = "int"


@dataclass
class ExpressionUniOp(Expression):
    operator: str
    argument: Expression
    ty: str | None = None

    def type_check(self):
        self.argument.type_check()
        if self.operator in ["boolean-negation"] and self.argument.ty != "bool":
            raise TypeCheckError(self.argument, self.argument.ty, "bool")
        elif self.operator in ["bitwise-negation", "opposite"] and self.argument.ty != "int":
            raise TypeCheckError(self.argument, self.argument.ty, "int")
        self.ty = self.argument.ty

@dataclass
class ExpressionBinOp(Expression):
    operator: str
    left: Expression
    right: Expression
    ty: str | None = None

    def type_check(self):
        self.left.type_check()
        self.right.type_check
        if self.operator in ["boolean-and", "boolean-or"]:
            if self.left.ty != "bool":
                raise TypeCheckError(self.left, self.left.ty, "bool")
            elif self.right.ty != "bool":
                raise TypeCheckError(self.right, self.right.ty, "bool")
            self.ty = "bool"
        if self.right.ty != "int":
            raise TypeCheckError(self.right, self.right.ty, "int")
        if self.left.ty != "int":
            raise TypeCheckError(self.left, self.left.ty, "int")
        if self.operator in ["equals", "notequals", "lt", "lte", "gt", "gte"]:
            self.ty = "bool"
        else:
            self.ty = "int"
        
@dataclass
class ExpressionCall(Expression):
    target: str
    arguments: List[Expression]
    ty: str | None = None

    def type_check(self):
        # for now the only call is print which has null return
        self.ty = "null"


@dataclass
class Statement:
    
    @abstractmethod
    def type_check(self):
        pass


@dataclass
class Block:
    stmts: List[Statement]

    def type_check(self) -> bool:
        successful = True
        for stmt in stmts:
            try: 
                stmt.type_check()
            except TypeCheckError:
                print(TypeCheckError)
                successful = False
        return successful

@dataclass
class StatementDecl(Statement):
    name: str
    type: str
    init: Expression

    def type_check(self):
        self.init.type_check()


@dataclass
class StatementAssign(Statement):
    lvalue: str  # TODO refactor for general grammar later
    rvalue: Expression

    def type_check(self):
        self.rvalue.type_check()

@dataclass
class StatementEval(Statement):
    expr: Expression

    def type_check(self):
        self.expr.type_check()

@dataclass
class StatementIf(Statement):
    cond: Expression
    body: Block
    elseblock: None | Block

    def type_check(self):
        self.cond.type_check()
        if self.cond.ty != "bool":
            raise TypeCheckError(self.cond, self.cond.ty, "bool")
        self.body.type_check()
        if self.elseblock is not None:
            self.body.type_check() and self.elseblock.type_check()

@dataclass
class StatementWhile(Statement):
    cond: Expression
    body: Block

    def type_check(self) -> bool:
        self.cond.type_check()
        if self.cond.ty != "bool":
            raise TypeCheckError(self.cond, self.cond.ty, "bool")
        self.body.type_check()

@dataclass
class Function:
    name: str
    body: Block

    def type_check(self)->bool:
        return self.body.type_check()

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

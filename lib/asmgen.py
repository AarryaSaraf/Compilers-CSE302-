from .tac import *

OPCODE_TO_ASM = {
    "add": "addq",
    "sub": "subq",
    "mul": "imulq",
    "and": "andq",
    "or": "orq",
    "xor": "xorq",
    "not": "notq",
    "neg": "negq",
    "lshift": "salq",
    "rshift": "sarq",
}
CC_REG_ORDER = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
SIMPLE_BIN_OPS = {"add", "sub", "mul", "and", "or", "xor"}
SIMPLE_UN_OPS = {"not", "neg"}


def global_symbs(decls: List[StatementDecl | Function]):
    globs = ""
    for decl in decls:
        globs += f".globl {decl.name}\n"
    return globs


def make_data_section(globvars: List[StatementDecl]):
    data_section = ".data\n"
    for decl in globvars:
        data_section += f"{decl.name}:\t .quad {decl.init}\n"
    return data_section


def make_text_section(asms: List[str]):
    text_section = ".text\n"
    for asm in asms:
        text_section += asm
    return text_section


class AsmGen:
    def __init__(self, proc: TACProc):
        self.proc = proc
        self.tac = proc.body
        self.temps = proc.body.get_tmps()
        self.tmp_alloc = {param: i for i, param in enumerate(self.proc.params)} | {
            tmp: i + len(proc.params) for i, tmp in enumerate(self.temps)
        }
        self.skeleton = f"""
{proc.name}: 
    pushq %rbp # store old RBP at top of the stack
    movq %rsp, %rbp # make RBP point to just after stack slots
    # At that point, we are 16-byte aligned
    # - return address (8 bytes) + copy of old RBP (8 bytes)
    # Now we allocate stack slots in units of 8 bytes (= 64 bits)
    # E.g., for 8 slots, i.e., 8 * 8 = 64 bytes
{self.compile_proc_head()}
__BODY__

        """
        # TODO: add handling for passed arguments
        self.body = ""

    def compile_proc_head(self):
        head_code = ""
        #  Ensure 16-bit alignment
        if len(self.tmp_alloc) % 2 == 0:
            head_code += f"    subq ${8*len(self.tmp_alloc)}, %rsp\n"
        else:
            # allocate an additional stack slot if not even
            head_code += f"    subq ${8*(len(self.tmp_alloc)+1)}, %rsp\n"
        for i, param in enumerate(self.proc.params):
            if i < 6:
                head_code += self.store_var(CC_REG_ORDER[i], param)
            else:
                head_code += f"    movq +{16+(i-6)*8}(%rbp), %rax\n"
                head_code += self.store_var("rax", param)
        return head_code

    def compile(self):
        for op in self.tac.ops:
            if not isinstance(op, TACLabel):
                self.body += "    /* " + op.pretty() + "*/\n"
            match op:
                case TACLabel(name):
                    self.body += f"{name}:\n"
                case TACOp("ret", [val], None) if isinstance(val, int):
                    self.body += f"   movq ${val}, %rax \n"
                    self.body += "    movq %rbp, %rsp # restore old RSP\n"
                    self.body += "    popq %rbp # restore old RBP\n"
                    self.body += "    retq \n"
                case TACOp("ret", [val], None) if isinstance(val, (TACTemp, TACGlobal)):
                    self.body += self.load_var(val, "rax")
                    self.body += "    movq %rbp, %rsp # restore old RSP\n"
                    self.body += "    popq %rbp # restore old RBP\n"
                    self.body += "    retq \n"
                case TACOp("ret", [], None):
                    self.body += "    xorq %rax, %rax# set return code to 0\n"
                    self.body += "    movq %rbp, %rsp # restore old RSP\n"
                    self.body += "    popq %rbp # restore old RBP\n"
                    self.body += "    retq\n "
                case TACOp("jmp", [label], None):
                    self.body += f"    jmp {label.name}\n"
                case TACOp("param", [i, arg], None) if i < 7:
                    self.body += self.load_var(arg, CC_REG_ORDER[i - 1])
                case TACOp(
                    "param", [i, arg], None
                ) if i >= 7:  # This assumes that we order the param calls in reverse during TAC generation
                    self.body += self.load_var(arg, "rax")
                    self.body += "    pushq %rax\n"
                case TACOp("call", _, _):
                    self.compile_call(op) #  this is a bit more complicated
                case TACOp(
                    "jz" | "jnz" | "jl" | "jle" | "jnl" | "jnle" as op,
                    [arg, label],
                    None,
                ):
                    self.body += self.load_var(arg, "rax")
                    self.body += f"    cmpq $0, %rax\n"
                    self.body += f"    {op} {label.name}\n"
                case TACOp("lshift" | "rshift" as op, [tmp1, tmp2], res):
                    self.body += self.load_var(tmp1, "rax")
                    self.body += self.load_var(tmp2, "rcx")
                    self.body += f"    {OPCODE_TO_ASM[op]} %cl, %rax\n"
                    self.body += self.store_var("rax", res)
                case TACOp("mod" | "div" as op, [tmp1, tmp2], res):
                    self.body += self.load_var(tmp1, "rax")
                    self.body += "    cqto\n"
                    self.body += self.load_var(tmp2, "rbx")
                    self.body += "    idivq %rbx\n"
                    if op == "mod":
                        self.body += self.store_var("rdx", res)
                    else:
                        self.body += self.store_var("rax", res)
                case TACOp(op, [tmp1, tmp2], res) if op in SIMPLE_BIN_OPS:
                    # TODO: these can be optimized with dereference
                    self.body += self.load_var(tmp1, "rax")
                    self.body += f"    {OPCODE_TO_ASM[op]} {self.to_addr(tmp2)}, %rax\n"
                    self.body += self.store_var("rax", res)
                case TACOp(op, [tmp], res) if op in SIMPLE_UN_OPS:
                    self.body += self.load_var(tmp, "rax")
                    self.body += f"    {OPCODE_TO_ASM[op]} %rax\n"
                    self.body += self.store_var("rax", res)
                case TACOp("print", [tmp], _):
                    self.body += self.load_var(tmp, "rdi")
                    self.body += "    callq bx_print_int\n"
                case TACOp("copy", [arg], res):
                    self.body += self.load_var(arg, "rax")
                    self.body += self.store_var("rax", res)
                case TACOp("const", [val], res):
                    self.body += (
                        f"    movq ${val}, -{(self.tmp_alloc[res]+1)*8}(%rbp)\n"
                    )
                case x:
                    print(f"WARNING: Cannot compile {x}")
        return self.skeleton.replace("__BODY__", self.body)

    def load_var(self, tmp: TACTemp | TACGlobal, dest):
        if isinstance(tmp, TACTemp):
            return f"    movq -{(self.tmp_alloc[tmp]+1)*8}(%rbp), %{dest}\n"
        elif isinstance(tmp, TACGlobal):
            return f"    movq {tmp.name}(%rip) , %{dest}\n"

    def store_var(self, reg, tmp: TACTemp | TACGlobal):
        if isinstance(tmp, TACTemp):
            return f"    movq %{reg}, -{(self.tmp_alloc[tmp]+1)*8}(%rbp)\n"
        if isinstance(tmp, TACGlobal):
            return f"    movq %{reg}, -{tmp.name}(%rip)\n"

    def to_addr(self, tmp: TACTemp):
        if isinstance(tmp, TACTemp):
            return f"-{(self.tmp_alloc[tmp]+1)*8}(%rbp)"
        elif isinstance(tmp, TACGlobal):
            return f"{tmp.name}(%rip)"

    def compile_call(self, op: TACOp) -> str:
        callee = op.args[0]
        args = op.args[1:]
        res = op.result
        # stack alignment
        if len(args)> 6 and len(args) % 2 != 0:
            print("inserting dummy for alingment")
            self.body += f"    pushq $0\n"
        # allocate arguments according to CC
        for i, arg in enumerate(args[:6]):
            self.body += self.load_var(arg, CC_REG_ORDER[i])
        for arg in reversed(args[6:]):
            self.body += self.load_var(arg, "rax")
            self.body += "    pushq %rax\n"

        # actual call
        self.body += f"    callq {callee}\n"
        # restore stack
        if len(args) > 6:
            if len(args) % 2 != 0:
                # in this case we pushed one more
                self.body += f"    addq ${(len(args)-5)*8}, %rsp\n"
            else:
                self.body += f"    addq ${(len(args)-6)*8}, %rsp\n"
        # store result
        if res is not None:
            self.body += self.store_var("rax", res)
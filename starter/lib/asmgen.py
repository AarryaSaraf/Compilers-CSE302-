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
    "rshift": "sarq"
}
SIMPLE_BIN_OPS = {"add", "sub", "mul", "and", "or", "xor"}
SIMPLE_UN_OPS = {"not", "neg"}
class AsmGen:
    def __init__(self, tacs: TAC):
        self.tac = tacs
        self.temps = tacs.get_tmps()
        self.tmp_alloc = {tmp: i for i, tmp in enumerate(self.temps)}
        self.skeleton = f"""
.globl main
.text
main:
    pushq %rbp # store old RBP at top of the stack
    movq %rsp, %rbp # make RBP point to just after stack slots
    # At that point, we are 16-byte aligned
    # - return address (8 bytes) + copy of old RBP (8 bytes)
    # Now we allocate stack slots in units of 8 bytes (= 64 bits)
    # E.g., for 8 slots, i.e., 8 * 8 = 64 bytes
    # -- MODIFY AS NEEDED --
    subq ${8*len(self.tmp_alloc)}, %rsp
__BODY__
    movq %rbp, %rsp # restore old RSP
    popq %rbp # restore old RBP
    movq $0, %rax # set return code to 0
    retq 
        """
        self.body = ""

    def compile(self):
        for op in self.tac.ops:
            match op:
                case TACLabel(name):
                    self.body += f"{name}:"
                case TACOp("lshift" | "rshift" as op, [tmp1, tmp2], res):
                    self.body += self.load_var(tmp1, "rax")
                    self.body += self.load_var(tmp2, "rcx")
                    self.body += f"   {OPCODE_TO_ASM[op]} %cl, %rax\n"
                    self.body += self.store_var("rax", res)
                case TACOp("mod" | "div" as op , [tmp1, tmp2], res):
                    self.body += self.load_var(tmp1, "rax")
                    self.body += self.load_var(tmp2, "rbx")
                    self.body += "    idivq %rbx\n"
                    if op == "mod":
                        self.body += self.store_var("rdx", res)
                    else:
                        self.body += self.store_var("rax", res)
                case TACOp(op, [tmp1, tmp2], res) if op in SIMPLE_BIN_OPS:
                    # TODO: these can be optimized with dereference
                    self.body += self.load_var(tmp1, "rax")
                    self.body += self.load_var(tmp2, "rbx")
                    self.body += f"    {OPCODE_TO_ASM[op]} %rbx, %rax\n"
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
                    self.body += f"    movq ${val}, {(self.tmp_alloc[res.num]+1)*8}(%rsp)\n"
                case x:
                    print(f"WARNING: Cannot compile {x}")
        return self.skeleton.replace("__BODY__", self.body)
    
    def load_var(self, tmp:TACTemp, dest):
        return f"    movq -{(self.tmp_alloc[tmp.num]+1)*8}(%rsp), %{dest}\n"
    
    def store_var(self, reg , tmp:TACTemp):
        return f"    movq %{reg}, -{(self.tmp_alloc[tmp.num]+1)*8}(%rsp)\n"
   
    
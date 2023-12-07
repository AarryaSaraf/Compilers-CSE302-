from .tac import *
from .alloc import AllocRecord, MemorySlot, Register, StackSlot
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
CALLEE_SAVE = ["rbx", "r12", "r13", "r14", "r15"]
CALLER_SAVE = ["rax", "rdi", "rdi", "rdx", "rcx", "r8", "r9","10", "r11"]

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


class AllocAsmGen:
    """
    x86 generation with allocated registers
    """
    def __init__(self, proc: TACProc, alloc: AllocRecord):
        self.proc = proc
        self.alloc = alloc
        self.tac = proc.body
        self.temps = proc.body.get_tmps()
        
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

    def compile_proc_head(self) -> str:
        head_code = ""
        head_code += f"{self.proc.name}:"
        head_code += "    pushq %rbp # store old RBP at top of the stack"
        head_code += "    movq %rsp, %rbp # make RBP point to just after stack slots"

        #  Ensure 16-bit alignment
        if len(self.alloc.stacksize) % 2 == 0:
            head_code += f"    subq ${8*self.alloc.stacksize}, %rsp\n"
        else:
            # allocate an additional stack slot if not even
            head_code += f"    subq ${8*(self.alloc.stacksize+1)}, %rsp\n"
        head_code += "# save callee save registers"
        # TODO only include the actually used registers
        for reg in CALLEE_SAVE:
            head_code += f"    pushq %{reg}"
        return head_code

    def proc_end(self) -> str:
        # TODO only include the actually used registers
        end_code = ""
        for reg in reversed(CALLEE_SAVE):
            end_code += f"    popq %{reg}"
        end_code += "    movq %rbp, %rsp # restore old RSP\n"
        end_code += "    popq %rbp # restore old RBP\n"
        end_code += "    retq \n"
    def compile(self):
        for op in self.tac.ops:
            if not isinstance(op, TACLabel):
                self.body += "    /* " + op.pretty() + "*/\n"
            match op:
                case TACLabel(name):
                    self.body += f"{name}:\n"
                case TACOp("ret", [val], None) if isinstance(val, int):
                    self.body += f"   movq ${val}, %rax \n"
                    self.body += self.proc_end()
                case TACOp("ret", [val], None) if isinstance(val, (TACTemp, TACGlobal)):
                    self.body += self.load_var(val, "rax")
                    self.body += self.proc_end()
                case TACOp("ret", [], None):
                    self.body += "    xorq %rax, %rax # set return code to 0\n"
                    self.body += self.proc_end()
                case TACOp("jmp", [label], None):
                    self.body += f"    jmp {label.name}\n"
                case TACOp("param", [i, arg], None) if i < 7:
                    self.body += self.load_var(arg, CC_REG_ORDER[i - 1])
                case TACOp(
                    "param", [i, arg], None
                ) if i >= 7:  # This assumes that we order the param calls in reverse during TAC generation
                    self.body += f"    pushq {self.to_address(arg)}\n"
                case TACOp("call", _,):
                    self.compile_call(op) # this gets a little bit complicated
                case TACOp(
                    "jz" | "jnz" | "jl" | "jle" | "jnl" | "jnle" as op,
                    [arg, label],
                    None,
                ):
                    self.body += f"    cmpq $0, {self.to_address(arg)}\n"
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
                    if self.alloc.mapping[tmp1] == self.alloc.mapping[res] and isinstance(self.alloc.mapping[res], Register):
                        self.body += f"    {OPCODE_TO_ASM[op]} {self.to_address(tmp2)}, {self.to_address}\n"
                    else:
                        self.body += self.load_var(tmp1, "rax")
                        self.body += f"    {OPCODE_TO_ASM[op]} {self.to_address(tmp2)}, %rax\n"
                        self.body += self.store_var("rax", res)
                case TACOp(op, [tmp], res) if op in SIMPLE_UN_OPS:
                    self.body += f"    {OPCODE_TO_ASM[op]} {self.to_address(tmp)}\n"
                case TACOp("copy", [arg], res):
                    self.body += self.load_var(arg, "r11")
                    self.body += self.store_var("r11", res)
                case TACOp("const", [val], res):
                    self.body += (
                        f"    movq ${val}, {self.to_address(res)}\n"
                    )
                case x:
                    print(f"WARNING: Cannot compile {x}")
        return self.compile_proc_head() + self.body

    def load_var(self, var, reg) -> str:
        slot = self.alloc[var]
        
        if isinstance(slot, StackSlot):
            return f"    movq {slot.offset}(%rbp), %{reg}"
        if isinstance(slot, Register):
            if slot.name == reg:
                return ""
            return f"    movq %{slot.name}, %{reg}"

    def to_address(self, var) -> str:
        slot = self.alloc[var]
        if isinstance(slot, StackSlot):
            return f"{slot.offset}(%rbp)"
        if isinstance(slot, Register):
            return f"%{slot.name}"
    
    def store_var(self, var, reg) -> str:
        slot = self.alloc[var]
        if isinstance(slot, StackSlot):
            return f"    movq %{reg}, {slot.offset}(%rbp)"
        if isinstance(slot, Register):
            if slot.name == reg:
                return ""
            return f"    movq %{reg}, %{slot.name}"

    def compile_call(self, op: TACOp) -> str:
        # We use a single call instruction this makes it easier 
        # to handle caller-save registers as they have to be pushed 
        # before the function arguments
        callee = op.args[0]
        args = op.args[1:]
        res = op.result
        # store caller-save registers
        used_registers = [
            self.alloc.mapping[var] 
            for var in op.live_out.intersection(op.live_in) # we look for all variables that have to stay alive throughout the call
            if isinstance(self.alloc.mapping[var], Register) and self.alloc.mapping[var] in CALLER_SAVE
        ]
        for reg in used_registers:
            self.body += f"    pushq %{reg}\n"
        # stack alignment
        if max(len(args)-6, 0)+ len(used_registers) % 2 != 0:
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
        
        # restore caller-save registers
        for reg in reversed(used_registers):
            self.body += f"    popq %{reg}\n"
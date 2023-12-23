from .tac import *
from .alloc import AllocRecord, MemorySlot, Register, StackSlot, DataSlot

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
CALLER_SAVE = ["rax", "rdi", "rdi", "rdx", "rcx", "r8", "r9", "10", "r11"]


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

    Args:
        proc: The TAC procedure we are compiling
        alloc: A record of the variables and their physical location
    """

    def __init__(self, proc: TACProc, alloc: AllocRecord):
        self.proc = proc
        self.alloc = alloc
        self.tac = proc.body
        self.body = ""
        self.reg_used = list(
            {
                slot.name
                for slot in self.alloc.mapping.values()
                if isinstance(slot, Register)
            }
        )

    def compile_proc_head(self) -> str:
        """
        Helper to compile the prologue of a function including saving callee saved registers,
            allocating the stack (+ stack alignment) and moving the function parameters if necessary.

        Returns:
            str: The procedure start
        """
        head_code = ""
        head_code += f"{self.proc.name}:\n"
        head_code += "    pushq %rbp # store old RBP at top of the stack\n"
        head_code += "    movq %rsp, %rbp # make RBP point to just after stack slots\n"

        #  Ensure 16-bit alignment
        if self.alloc.stacksize % 2 == 0:
            head_code += f"    subq ${8*self.alloc.stacksize}, %rsp\n"
        else:
            # allocate an additional stack slot if not even
            head_code += f"    subq ${8*(self.alloc.stacksize+1)}, %rsp\n"
        head_code += "    # save callee save registers\n"

        # save callee save registers if used
        save_registers = [reg for reg in self.reg_used if reg in CALLEE_SAVE]

        for reg in save_registers:
            head_code += f"    pushq %{reg}\n"
        if len(save_registers) % 2 != 0:
            head_code += f"    movq $0, %r11\n    pushq %r11\n"  # push one more to have 16 byte alignment (callee saves are uneven)

        head_code += "    # move parameters to allocated slots (if necessary)\n"
        # if parameter variables are not allocated to CC Registers move them:
        for i, param in enumerate(self.proc.params):
            if i < 6 and self.get_location(param) != Register(CC_REG_ORDER[i]):
                head_code += f"    movq %{CC_REG_ORDER[i]}, {self.to_address(param)}"
            if i >= 6 and self.get_location(param) != StackSlot(16 + (i - 6) * 8):
                head_code += f"    movq {16+(i-6)*8}(%rsp), {self.to_address(param)}"

        return head_code

    def proc_end(self) -> str:
        """
        Helper to compile the epilogue of a function including restoring callee saved registers
            and resetting the rsp/rbp

        Returns:
            str: The procedure end
        """
        end_code = ""

        # restore callee save registers if used
        save_registers = [reg for reg in self.reg_used if reg in CALLEE_SAVE]
        if len(save_registers) % 2 != 0:
            end_code += f"    popq %{save_registers[-1]}\n"  # pop one more to have 16 byte alignment (callee saves are uneven) also we override r15 anyway

        for reg in reversed(save_registers):
            end_code += f"    popq %{reg}\n"

        end_code += "    movq %rbp, %rsp # restore old RSP\n"
        end_code += "    popq %rbp # restore old RBP\n"
        end_code += "    retq\n"
        return end_code

    def compile(self):
        """
        Generates x86 code from the allocated TAC

        Returns:
            str: Compiled assembly code
        """
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
                case TACOp(
                    "call",
                    _,
                ):
                    self.compile_call(op)  # this gets a little bit complicated
                case TACOp(
                    "jz" | "jnz" | "jl" | "jle" | "jnl" | "jnle" as op,
                    [arg, label],
                    None,
                ):
                    self.body += f"    cmpq $0, {self.to_address(arg)}\n"
                    self.body += f"    {op} {label.name}\n"
                case TACOp("lshift" | "rshift" as op, [tmp1, tmp2], res):
                    self.body += self.load_var(tmp1, "r11")
                    self.body += self.load_var(tmp2, "rcx")
                    self.body += f"    {OPCODE_TO_ASM[op]} %cl, %r11\n"
                    self.body += self.store_var("r11", res)
                case TACOp("mod" | "div" as opcode, [tmp1, tmp2], res):
                    print([self.get_location(tmp) for tmp in op.live_out])
                    self.body += self.load_var(tmp1, "rax")
                    self.body += "    cqto\n"
                    self.body += self.load_var(tmp2, "rbx")
                    self.body += "    idivq %rbx\n"
                    if opcode == "mod":
                        self.body += self.store_var("rdx", res)
                    else:
                        self.body += self.store_var("rax", res)
                case TACOp(op, [tmp1, tmp2], res) if op in SIMPLE_BIN_OPS:
                    if self.get_location(tmp1) == self.get_location(res) and isinstance(self.get_location(res), Register):
                        self.body += f"    {OPCODE_TO_ASM[op]} {self.to_address(tmp2)}, {self.to_address(tmp1)}\n"
                    else:
                        self.body += self.load_var(tmp1, "r11")
                        self.body += (
                            f"    {OPCODE_TO_ASM[op]} {self.to_address(tmp2)}, %r11\n"
                        )
                        self.body += self.store_var("r11", res)
                case TACOp(op, [tmp], res) if op in SIMPLE_UN_OPS:
                    self.body += f"    {OPCODE_TO_ASM[op]} {self.to_address(tmp)}\n"
                case TACOp("copy", [arg], res):
                    if  self.get_location(arg )== self.get_location(res):
                        continue
                    if  isinstance(self.get_location(arg), Register) or isinstance(
                        self.get_location(res), Register
                    ):
                        self.body += (
                            f"    movq {self.to_address(arg)}, {self.to_address(res)}\n"
                        )
                    else:  # we can't move memory to memory
                        self.body += self.load_var(arg, "r11")
                        self.body += self.store_var("r11", res)
                case TACOp("const", [val], res):
                    self.body += f"    movq ${val}, {self.to_address(res)}\n"
                case x:
                    print(f"WARNING: Cannot compile {x}")
        return self.compile_proc_head() + self.body

    def load_var(self, var: TACTemp | TACGlobal, reg: str) -> str:
        """
        Helper to load a variable into a register

        Args:
            var: The variable to be loaded
            reg: The register the variable should be loaded in

        Return
            str: The compiled instructions to move the variable
        """
        if isinstance(var, TACTemp):
            slot = self.alloc.mapping[var]

            if isinstance(slot, StackSlot):
                return f"    movq {slot.offset}(%rbp), %{reg}\n"
            if isinstance(slot, Register):
                if slot.name == reg:
                    return ""
                return f"    movq %{slot.name}, %{reg}\n"
        elif isinstance(var, TACGlobal):
            return f"    movq {var.name}(%rip) , %{reg}\n"
        elif isinstance(var, int):
            return f"    movq ${var}, %{reg}\n"


    def to_address(self, var: TACTemp) -> str:
        """
        Format the address of a variable
        """
        if isinstance(var, TACTemp):
            slot = self.alloc.mapping[var]
            if isinstance(slot, StackSlot):
                return f"{slot.offset}(%rbp)"
            if isinstance(slot, Register):
                return f"%{slot.name}"
        elif isinstance(var, TACGlobal):
            return f"{var.name}(%rip)"
        elif isinstance(var, int):
            return f"${var}"

    def store_var(self, reg: str, var: TACTemp | TACGlobal) -> str:
        """
        Helper to stored a register in a variable

        Args:
            reg: The register whose value should be stored
            var: The variable in whose location the register's value should be saved

        Return
            str: The compiled instructions to move the variable
        """
        if isinstance(var, TACTemp):
            slot = self.alloc.mapping[var]
            if isinstance(slot, StackSlot):
                return f"    movq %{reg}, {slot.offset}(%rbp)\n"
            if isinstance(slot, Register):
                if slot.name == reg:
                    return ""
                return f"    movq %{reg}, %{slot.name}\n"
        elif isinstance(var, TACGlobal):
            return f"    movq %{reg}, {var.name}(%rip)\n"
            

    def get_location(self, var) -> MemorySlot:
        if isinstance(var, TACTemp):
            return self.alloc.mapping[var]
        elif isinstance(var, TACGlobal):
            return DataSlot(var.name)
        
    def compile_call(self, op: TACOp) -> str:
        """
        Utitility function to compile call instructions

        Args:
            op (TACOp): The Call instruction to be compiled

        Return:
            str: The compiled call
        """
        # We use a single call instruction this makes it easier
        # to handle caller-save registers as they have to be pushed
        # before the function arguments
        callee = op.args[0]
        args = op.args[1:]
        res = op.result
        # store caller-save registers
        used_registers = [
            self.get_location(var)
            for var in op.live_out.intersection(
                op.live_in
            )  # we look for all variables that have to stay alive throughout the call
            if isinstance(self.get_location(var), Register)
            and self.get_location(var).name in CALLER_SAVE
        ]
        stack_offset = 0 # to keep track of the stack pointer
        for reg in used_registers:
            self.body += f"    pushq %{reg.name}\n"
            stack_offset +=1
        # stack alignment
        if max(len(args) - 6, 0) + len(used_registers) % 2 != 0:
            self.body += f"    movq $0, %r11\n    pushq %r11\n"
            stack_offset +=1 
        # allocate arguments according to CC
        for i, arg in enumerate(args[:6]):
            # if we pushed the variable take it from the stack (this also avoids any unwanted overrides to rdi etc.)
            if self.get_location(arg) in used_registers:
                pushed_index = used_registers.index(self.get_location(arg)) 
                self.body += f"    movq {stack_offset -pushed_index}(%rsp), %{CC_REG_ORDER[i]}\n" # i hope this math is correct
            else:
                self.body += self.load_var(arg, CC_REG_ORDER[i])
        for arg in reversed(args[6:]):
            # if we pushed the variable take it from the stack (this also avoids any unwanted overrides to rdi etc.)
            if self.get_location(arg) in used_registers:
                pushed_index = used_registers.index(self.get_location(arg)) 
                self.body += f"    movq {stack_offset -pushed_index}(%rsp), %r11\n"
            else:
                self.body += self.load_var(arg, "r11")
            self.body += "    pushq %r11\n"
            stack_offset += 1

        # actual call
        self.body += f"    callq {callee}\n"

        # remove alignment buffer if inserted
        if max(len(args) - 6, 0) + len(used_registers) % 2 != 0:
            self.body += f"    addq $8, %rsp\n"
        # restore stack
        if len(args) > 6:
            self.body += f"    addq ${(len(args)-6)*8}, %rsp\n"

        # store result
        if res is not None:
            self.body += self.store_var("rax", res)

        # restore caller-save registers
        for reg in reversed(used_registers):
            self.body += f"    popq %{reg.name}\n"

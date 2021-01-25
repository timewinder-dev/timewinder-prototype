import dis
import operator

from typing import Any
from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .interpreter import Interpreter


class OpcodeInterpreter:
    def __init__(self, proc: "Interpreter", instructions):
        self.proc = proc
        self.stack: List[Any] = []
        self.instructions: List[dis.Instruction] = instructions
        self.pc = 0

    def push_stack(self, v: Any):
        self.stack.append(v)

    def pop_stack(self) -> Any:
        assert len(self.stack) > 0
        v = self.stack[-1]
        self.stack = self.stack[:-1]
        return v

    def find_pc_for_offset(self, offset):
        for i, x in enumerate(self.instructions):
            if x.offset == offset:
                return i

    def interpret_instruction(self) -> bool:
        inst = self.instructions[self.pc]
        methodname = "exec_" + inst.opname.lower()
        try:
            method = self.__getattribute__(methodname)
            ret = method(inst)
        except AttributeError as e:
            print(e)
            return self._exec_debug(inst)
        if ret is None:
            self.pc += 1
            return True
        return ret

    def _exec_debug(self, inst):
        self.proc.debug_print()
        raise NotImplementedError(
            f"instructions of type {inst.opname} aren't supported yet"
        )

    def exec_load_const(self, inst):
        self.push_stack(inst.argval)

    def exec_load_fast(self, inst):
        self.push_stack(self.proc.resolve_var(inst.argval))

    def exec_load_global(self, inst):
        val = self.proc.resolve_global(inst.argval)
        self.push_stack(val)

    def exec_load_attr(self, inst):
        val = self.proc.resolve_getattr(self.pop_stack(), inst.argval)
        self.push_stack(val)

    def exec_store_fast(self, inst):
        self.proc.on_store_fast(inst.argval, self.pop_stack())

    def exec_store_attr(self, inst):
        tos = self.pop_stack()
        tos1 = self.pop_stack()
        self.proc.resolve_setattr(tos, inst.argval, tos1)

    def exec_nop(self, inst):
        pass

    def exec_store_subscr(self, inst):
        tos = self.pop_stack()
        tos1 = self.pop_stack()
        tos2 = self.pop_stack()
        tos1[tos] = tos2

    def exec_call_function(self, inst):
        args = []
        for i in range(inst.argval):
            args.append(self.pop_stack())
        args.reverse()
        func = self.pop_stack()
        # Delegate to the process to do the rest
        ret = self.proc.on_call_function(func, args)
        self.push_stack(ret)

    def exec_pop_top(self, inst):
        self.pop_stack()

    def exec_binary_add(self, inst):
        self._exec_binop(inst, operator.add)

    def exec_binary_subtract(self, inst):
        self._exec_binop(inst, operator.sub)

    def _exec_binop(self, inst, op):
        tos = self.pop_stack()
        tos1 = self.pop_stack()
        self.push_stack(op(tos1, tos))

    def exec_compare_op(self, inst):
        tos = self.pop_stack()
        tos1 = self.pop_stack()
        if inst.argval == "==":
            self.push_stack(tos1 == tos)
        elif inst.argval == "!=":
            self.push_stack(tos1 != tos)
        elif inst.argval == "<":
            self.push_stack(tos1 < tos)
        elif inst.argval == ">":
            self.push_stack(tos1 > tos)
        elif inst.argval == "<=":
            self.push_stack(tos1 <= tos)
        elif inst.argval == ">=":
            self.push_stack(tos1 >= tos)
        else:
            self.proc.debug_print()
            assert False, f"unknown operator {inst.argval}"

    def exec_pop_jump_if_false(self, inst):
        if not self.pop_stack():
            self.pc = self.find_pc_for_offset(inst.argval)
            return True
        return None

    def exec_pop_jump_if_true(self, inst):
        if self.pop_stack():
            self.pc = self.find_pc_for_offset(inst.argval)
            return True
        return None

    def exec_return_value(self, inst):
        self.pc = -1
        self.proc.on_return(self.pop_stack())
        return False

    def exec_yield_value(self, inst):
        self.proc.on_yield(self.stack[-1])
        self.pc += 1
        return False

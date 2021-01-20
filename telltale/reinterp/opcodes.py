import dis
import operator

from typing import Any
from typing import Callable
from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .process import ASTProcess


InterpretSig = Callable[["ASTProcess", dis.Instruction], None]


class OpcodeInterpreter:
    def __init__(self, proc: "ASTProcess"):
        self.proc = proc
        self.stack: List[Any] = []

    def interpret_instruction(self, inst: dis.Instruction):
        methodname = "exec_" + inst.opname.lower()
        try:
            method = self.__getattribute__(methodname)
            return method(inst)
        except AttributeError as e:
            print(e)
            pass
        return self._exec_debug(inst)

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
        self.push_stack(inst.argval)

    def exec_load_attr(self, inst):
        val = self.proc.resolve_getattr(self.pop_stack(), inst.argval)
        self.push_stack(val)

    def exec_store_fast(self, inst):
        self.proc.state[inst.argval] = self.pop_stack()

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
        name = self.pop_stack()
        # Delegate to the process to do the rest
        ret = self.proc.call_function(name, args)
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
        if inst.argval == "!=":
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
            assert False, "unknown operator"

    def exec_pop_jump_if_false(self, inst):
        if not self.pop_stack():
            return (True, self.proc.find_pc_for_offset(inst.argval))
        return

    def exec_pop_jump_if_true(self, inst):
        if self.pop_stack():
            return (True, self.proc.find_pc_for_offset(inst.argval))
        return

    def exec_return_value(self, inst):
        return (False, -1)

    def exec_yield_value(self, inst):
        self.proc.hit_yield(self.stack[-1])
        return (False, self.proc.pc + 1)

    def push_stack(self, v: Any):
        self.stack.append(v)

    def pop_stack(self) -> Any:
        assert len(self.stack) > 0
        v = self.stack[-1]
        self.stack = self.stack[:-1]
        return v
import dis
import operator
from timewinder.pause import Continue
from timewinder.pause import PauseReason

from typing import Any
from typing import List
from typing import Optional
from typing import Union
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .interpreter import Interpreter


ProgressType = Optional[Union[PauseReason, Continue]]


class OpcodeInterpreter:
    def __init__(self, proc: "Interpreter", instructions):
        self.proc = proc
        self.stack: List[Any] = []
        self.instructions: List[dis.Instruction] = instructions
        self.pc = 0

    def push_stack(self, v: Any):
        # As a debugging strategy, find when an unusual value is pushed on the
        # stack and start a breakpoint, right here.
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

    def interpret_instruction(self) -> Continue:
        inst = self.instructions[self.pc]
        methodname = "exec_" + inst.opname.lower()
        try:
            method = self.__getattribute__(methodname)
            ret: ProgressType = method(inst)
        except AttributeError as e:
            print(e)
            return self._exec_debug(inst)
        # Unify return types into Continue
        # None case
        out: Continue
        if ret is None:
            ret = PauseReason.NORMAL
        # Just PauseReason
        if isinstance(ret, Continue):
            out = ret
        else:
            out = Continue(ret)

        if out.kind == PauseReason.NORMAL:
            self.pc += 1
        elif out.kind == PauseReason.YIELD:
            self.pc += 1
        return out

    def _exec_debug(self, inst):
        self.proc.debug_print()
        raise NotImplementedError(
            f"instructions of type {inst.opname} aren't supported yet"
        )

    def exec_load_const(self, inst):
        self.push_stack(inst.argval)

    def exec_load_fast(self, inst):
        self.push_stack(self.proc.resolve_var_by_name(inst.argval))

    def exec_load_global(self, inst):
        val = self.proc.resolve_global(inst.argval)
        self.push_stack(val)

    def exec_load_attr(self, inst):
        val = self.proc.resolve_getattr(self.pop_stack(), inst.argval)
        self.push_stack(val)

    def exec_load_method(self, inst):
        tos = self.pop_stack()
        bound, method = self.proc.resolve_load_method(tos, inst.argval)
        if bound:
            self.push_stack(None)
            self.push_stack(method)
        else:
            self.push_stack(method)
            self.push_stack(tos)

    def exec_store_fast(self, inst):
        return self.proc.on_store_fast(inst.argval, self.pop_stack())

    def exec_store_attr(self, inst):
        tos = self.pop_stack()
        tos1 = self.pop_stack()
        return self.proc.on_setattr(tos, inst.argval, tos1)

    def exec_nop(self, inst):
        pass

    def exec_dup_top(self, inst):
        tos = self.pop_stack()
        self.push_stack(tos)
        self.push_stack(tos)

    def exec_store_subscr(self, inst):
        tos = self.pop_stack()
        tos1 = self.pop_stack()
        tos2 = self.pop_stack()
        tos1[tos] = tos2

    def exec_binary_subscr(self, inst):
        tos = self.pop_stack()
        tos1 = self.pop_stack()
        v = self.proc.resolve_var(tos1)
        self.push_stack(v[tos])

    def exec_build_slice(self, inst):
        tos = self.pop_stack()
        tos1 = self.pop_stack()
        if inst.argval == 2:
            self.push_stack(slice(tos1, tos))
        elif inst.argval == 3:
            tos2 = self.pop_stack()
            self.push_stack(slice(tos2, tos1, tos))
        else:
            assert False, "instruction has invalid argval"

    def exec_call_method(self, inst):
        args = []
        for i in range(inst.argval):
            args.append(self.pop_stack())
        args.reverse()
        tos = self.pop_stack()
        tos1 = self.pop_stack()
        if tos1 is None:
            ret = self.proc.resolve_call_function(tos, args)
        else:
            args.insert(0, tos)
            ret = self.proc.resolve_call_function(tos1, args)
        self.push_stack(ret)

    def exec_call_function(self, inst):
        args = []
        for i in range(inst.argval):
            args.append(self.pop_stack())
        args.reverse()
        func = self.pop_stack()
        # Delegate to the process to do the rest
        ret = self.proc.resolve_call_function(func, args)
        self.push_stack(ret)

    def exec_pop_top(self, inst):
        self.pop_stack()

    def exec_rot_two(self, inst):
        tos = self.pop_stack()
        tos1 = self.pop_stack()
        self.push_stack(tos)
        self.push_stack(tos1)

    def exec_binary_add(self, inst):
        self._exec_binop(inst, operator.add)

    def exec_binary_subtract(self, inst):
        self._exec_binop(inst, operator.sub)

    def exec_inplace_subtract(self, inst):
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
            return PauseReason.PC_JUMPED
        return PauseReason.NORMAL

    def exec_pop_jump_if_true(self, inst):
        if self.pop_stack():
            self.pc = self.find_pc_for_offset(inst.argval)
            return PauseReason.PC_JUMPED
        return PauseReason.NORMAL

    def exec_jump_absolute(self, inst):
        self.pc = self.find_pc_for_offset(inst.argval)
        return PauseReason.PC_JUMPED

    def exec_return_value(self, inst):
        self.pc = -1
        return self.proc.on_return(self.pop_stack())

    def exec_yield_value(self, inst):
        return Continue(PauseReason.YIELD, self.stack[-1])

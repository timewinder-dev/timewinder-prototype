import dis

from telltale.process import Process
from telltale.statetree import TreeType

from .interpreter import Interpreter

from typing import Callable


class BytecodeProcessClosure:
    def __init__(self, func: Callable):
        self.func = func
        self.instructions = list(dis.get_instructions(func))

    def __call__(self, *args, **kwargs):
        return BytecodeProcess(self, args, kwargs)


class BytecodeProcess(Process):
    def __init__(self, closure: BytecodeProcessClosure, in_args, in_kwargs):
        self._name = closure.func.__name__
        self.interp = Interpreter(closure.func, in_args, in_kwargs)

    @property
    def name(self) -> str:
        return self._name

    def can_execute(self) -> bool:
        if self.interp.pc < 0:
            return False
        return self.interp.pc < len(self.interp.instructions)

    def execute(self, state_controller):
        self.interp.state_controller = state_controller
        while self.interp.pc < len(self.interp.instructions):
            cont = self.interp.interpret_instruction()
            if not cont:
                break
        if self.interp.yielded is not None:
            self._name = self.interp.yielded
        self.interp.state_controller = None

    def get_state(self) -> TreeType:
        return {
            "state": self.interp.state,
            "stack": self.interp.ops.stack,
            "pc": self.interp.ops.pc,
            "_name": self._name,
        }

    def set_state(self, state: TreeType):
        assert isinstance(state, dict)
        self.interp.state = state["state"]
        self.interp.ops.stack = state["stack"]
        self.interp.ops.pc = state["pc"]
        self._name = state["_name"]

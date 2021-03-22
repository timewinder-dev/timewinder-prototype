from timewinder.process import Process
from timewinder.process import ProcessException
from timewinder.statetree import TreeType
from timewinder.pause import Continue
from timewinder.pause import PauseReason

from .interpreter import Interpreter

from typing import Callable


class BytecodeProcess(Process):
    def __init__(self, func: Callable, in_args=None, in_kwargs=None):
        self._name = func.__name__
        self.interp = Interpreter(func, in_args, in_kwargs)

    @property
    def name(self) -> str:
        return self._name

    def can_execute(self) -> bool:
        if self.interp.pc < 0:
            return False
        return self.interp.pc < len(self.interp.instructions)

    def execute(self, state_controller):
        self.interp.state_controller = state_controller
        cont = Continue()
        while self.interp.pc < len(self.interp.instructions):
            try:
                cont = self.interp.interpret_instruction()
            except Exception as e:
                raise ProcessException(f"{self.name}@{self.interp.pc}", e)
            if cont.kind == PauseReason.DONE or cont.kind == PauseReason.YIELD:
                break

        if cont.kind == PauseReason.YIELD:
            if cont.yield_msg != "":
                self._name = cont.yield_msg
        self.interp.state_controller = None
        return cont

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

    def __repr__(self) -> str:
        return f"{self._name}@{self.interp.ops.pc}: {self.interp.state}"

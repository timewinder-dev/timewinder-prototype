from timewinder.process import Process
from timewinder.process import ProcessException
from timewinder.statetree import CAS
from timewinder.statetree import Hash
from timewinder.statetree import TreeableType
from timewinder.pause import Continue
from timewinder.pause import PauseReason

from .interpreter import Interpreter

from typing import Callable
from typing import Optional


class BytecodeProcess(Process):
    def __init__(self, func: Callable, in_args=None, in_kwargs=None):
        self._funcname = func.__name__
        self._stepname = "start"
        self.interp = Interpreter(func, in_args, in_kwargs)
        self.set_hash: Optional[Hash] = None

    def on_register_evaluator(self, idx: int) -> None:
        self.interp.thread_idx = idx

    @property
    def name(self) -> str:
        return f"{self._funcname}@{self._stepname}"

    def can_execute(self) -> bool:
        if self.interp.pc < 0:
            return False
        return self.interp.pc < len(self.interp.instructions)

    def execute(self, state_controller):
        self.set_hash = None
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
                self._stepname = cont.yield_msg
        self.interp.state_controller = None
        return cont

    def register_cas(self, cas: CAS) -> None:
        self._cas = cas

    def get_state(self) -> TreeableType:
        if self.set_hash is not None:
            return self.set_hash
        save_state = {
            k: v for (k, v) in self.interp.state.items()
            if not k.startswith("_")
        }
        return {
            "state": save_state,
            "stack": self.interp.ops.stack,
            "pc": self.interp.ops.pc,
            "_stepname": self._stepname,
            "_funcname": self._funcname,
        }

    def set_state(self, hash: Hash):
        if hash == self.set_hash:
            return
        self.set_hash = hash
        state = self._cas.restore(hash)
        assert isinstance(state, dict)
        self.interp.state = state["state"]
        self.interp.ops.stack = state["stack"]
        self.interp.ops.pc = state["pc"]
        self._stepname = state["_stepname"]
        self._funcname = state["_funcname"]

    def __repr__(self) -> str:
        return f"{self.name}: {self.interp.state}"

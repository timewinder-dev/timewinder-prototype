import dis

from telltale.process import Process
from telltale.model import Model
from telltale.statetree import TreeType

from .bytecode import OpcodeStoreInterface
from .opcodes import OpcodeInterpreter

from typing import Any
from typing import Callable
from typing import Dict


MODEL_PREFIX = "__model__"


def _print_list(l, highlight):
    highlights = ["   "] * len(l)
    highlights[highlight] = "-> "
    print("\n".join(["%s%s" % x for x in zip(highlights, l)]))


class BytecodeProcessClosure:
    def __init__(self, func: Callable):
        self.func = func
        self.instructions = list(dis.get_instructions(func))

    def __call__(self, *args, **kwargs):
        return BytecodeProcess(self, args, kwargs)


class BytecodeProcess(Process, OpcodeStoreInterface):
    def __init__(self, closure: BytecodeProcessClosure, in_args, in_kwargs):
        self.func = closure.func
        self._name = self.func.__name__
        self.binds: Dict[str, Any] = {}
        self.state: Dict[str, Any] = {}
        if len(in_kwargs) != 0:
            raise NotImplementedError("Need keyword arg binding support")
        n_args = self.func.__code__.co_argcount
        argnames = list(self.func.__code__.co_varnames)[:n_args]
        for name, a in zip(argnames, in_args):
            if isinstance(a, Model):
                self.binds[name] = MODEL_PREFIX + a.name
            else:
                self.state[name] = a
        self.interp = OpcodeInterpreter(self, closure.instructions)

    @property
    def name(self) -> str:
        return self._name

    def can_execute(self) -> bool:
        if self.interp.pc < 0:
            return False
        return self.interp.pc < len(self.interp.instructions)

    def execute(self, state_controller):
        self.state_controller = state_controller
        while self.interp.pc < len(self.interp.instructions):
            cont = self.interp.interpret_instruction()
            if not cont:
                break
        self.state_controller = None

    def get_state(self) -> TreeType:
        return {
            "state": self.state,
            "stack": self.interp.stack,
            "pc": self.interp.pc,
            "_name": self._name,
        }

    def set_state(self, state: TreeType):
        assert isinstance(state, dict)
        self.state = state["state"]
        self.interp.stack = state["stack"]
        self.interp.pc = state["pc"]
        self._name = state["_name"]

    def call_function(self, name, args):
        print(f"TODO: Calling {name} with {args}")

    def on_yield(self, val):
        self._name = val

    def store_fast(self, name, val):
        self.state[name] = val

    def resolve_var(self, varname: str):
        if varname in self.state:
            return self.state[varname]
        if varname in self.binds:
            return self.binds[varname]
        raise LookupError(f"Couldn't find variable {varname}")

    def resolve_getattr(self, base, attr):
        if isinstance(base, str):
            if base.startswith(MODEL_PREFIX):
                model = self._get_from_tree(base)
                return getattr(model, attr)
        return getattr(base, attr)

    def resolve_setattr(self, base, attr, val):
        if isinstance(base, str):
            if base.startswith(MODEL_PREFIX):
                model = self._get_from_tree(base)
                return setattr(model, attr, val)
        return setattr(base, attr, val)

    def _get_from_tree(self, base):
        model_name = base[len(MODEL_PREFIX) :]
        return self.state_controller.tree[model_name]

    def debug_print(self):
        import pprint

        print("\n\nState:\n")
        pprint.pprint(self.state)
        print("\nInstructions:\n")
        _print_list(self.interp.instructions, self.interp.pc)
        print("\n\n")

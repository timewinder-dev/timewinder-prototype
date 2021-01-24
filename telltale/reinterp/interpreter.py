import dis

from telltale.model import Model

from .opcodes import OpcodeInterpreter

from typing import Any
from typing import Callable
from typing import Dict
from typing import List


MODEL_PREFIX = "__model__"


class Interpreter:
    def __init__(self, func: Callable, in_args=None, in_kwargs=None):
        self.func = func
        instructions = list(dis.get_instructions(self.func))
        self.ops = OpcodeInterpreter(self, instructions)
        self.binds: Dict[str, Any] = {}
        self.state: Dict[str, Any] = {}
        self.yielded = None
        self.return_val = None
        self.done = False

        # Set from the outside
        self.state_controller = None
        if in_kwargs is None:
            in_kwargs = {}
        if len(in_kwargs) != 0:
            raise NotImplementedError("Need keyword arg binding support")
        if in_args is None:
            in_args = []
        n_args = self.func.__code__.co_argcount
        argnames = list(self.func.__code__.co_varnames)[:n_args]
        for name, a in zip(argnames, in_args):
            if isinstance(a, Model):
                self.binds[name] = MODEL_PREFIX + a.name
            else:
                self.state[name] = a

    def interpret_instruction(self):
        return self.ops.interpret_instruction()

    def get_yield(self):
        y = self.yielded
        self.yielded = None
        return y

    def on_yield(self, val):
        self.yielded = val

    def on_return(self, val):
        self.done = True
        self.return_val = val

    def store_fast(self, name, val):
        self.state[name] = val

    def resolve_var(self, varname: str):
        if varname in self.state:
            return self.state[varname]
        if varname in self.binds:
            return self.binds[varname]
        raise LookupError(f"Couldn't find variable {varname}")

    @property
    def pc(self) -> int:
        return self.ops.pc

    @property
    def instructions(self) -> List:
        return self.ops.instructions

    def call_function(self, name, args):
        print(f"TODO: Calling {name} with {args}")

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
        assert self.state_controller is not None
        model_name = base[len(MODEL_PREFIX) :]
        return self.state_controller.tree[model_name]

    def debug_print(self):
        import pprint

        print("\n\nState:\n")
        pprint.pprint(self.state)
        print("\nInstructions:\n")
        _print_list(self.ops.instructions, self.ops.pc)
        print("\n\n")


def _print_list(l, highlight):
    highlights = ["   "] * len(l)
    highlights[highlight] = "-> "
    print("\n".join(["%s%s" % x for x in zip(highlights, l)]))

    highlights = ["   "] * len(l)
    highlights[highlight] = "-> "
    print("\n".join(["%s%s" % x for x in zip(highlights, l)]))

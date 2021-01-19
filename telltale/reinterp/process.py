import dis

from telltale.process import Process
from telltale.model import Model
from telltale.statetree import TreeType

from .opcodes import OpcodeInterpreter

from typing import Any
from typing import Callable
from typing import Dict


MODEL_PREFIX = "__model__"


def _print_list(l, highlight):
    highlights = ["   "] * len(l)
    highlights[highlight] = "-> "
    print("\n".join(["%s%s" % x for x in zip(highlights, l)]))


class ASTProcessClosure:
    def __init__(self, func: Callable):
        self.func = func
        self.instructions = list(dis.get_instructions(func))

    def __call__(self, *args, **kwargs):
        return ASTProcess(self, args, kwargs)


class ASTProcess(Process):
    def __init__(self, closure: ASTProcessClosure, in_args, in_kwargs):
        self.instructions = closure.instructions
        self.func = closure.func
        self._name = self.func.__name__
        self.binds: Dict[str, Any] = {}
        self.state: Dict[str, Any] = {}
        self.pc = 0
        if len(in_kwargs) != 0:
            raise NotImplementedError("Need keyword arg binding support")
        n_args = self.func.__code__.co_argcount
        argnames = list(self.func.__code__.co_varnames)[:n_args]
        for name, a in zip(argnames, in_args):
            if isinstance(a, Model):
                self.binds[name] = MODEL_PREFIX + a.name
            else:
                self.state[name] = a
        self.interp = OpcodeInterpreter(self)

    @property
    def name(self) -> str:
        return self._name

    def can_execute(self) -> bool:
        if self.pc < 0:
            return False
        return self.pc < len(self.instructions)

    def execute(self, state_controller):
        self.state_controller = state_controller
        while self.pc < len(self.instructions):
            ret = self.interp.interpret_instruction(self.instructions[self.pc])
            if ret is None:
                self.pc += 1
            else:
                cont, offset = ret
                self.pc = offset
                if not cont:
                    break
        self.state_controller = None

    def get_state(self) -> TreeType:
        return {
            "state": self.state,
            "stack": self.interp.stack,
            "pc": self.pc,
            "_name": self._name,
        }

    def set_state(self, state: TreeType):
        assert isinstance(state, dict)
        self.state = state["state"]
        self.interp.stack = state["stack"]
        self.pc = state["pc"]
        self._name = state["_name"]

    def call_function(self, name, args):
        print(f"TODO: Calling {name} with {args}")
        pass

    def hit_yield(self, val):
        self._name = val

    def resolve_var(self, varname):
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

    def find_pc_for_offset(self, offset):
        for i, x in enumerate(self.instructions):
            if x.offset == offset:
                return i

    def debug_print(self):
        import pprint

        print("\n\nState:\n")
        pprint.pprint(self.state)
        print("\nInstructions:\n")
        _print_list(self.instructions, self.pc)
        print("\n\n")

import builtins
import dis
import sys
import inspect
from dataclasses import dataclass

from timewinder.object import Object
from timewinder.pause import Continue
from timewinder.pause import PauseReason
from timewinder.pause import Fairness
from timewinder.generators import NonDeterministicSet

from .opcodes import OpcodeInterpreter

from typing import Any
from typing import Callable
from typing import Dict
from typing import List


OBJECT_PREFIX = "__object__"


# Method delegates called resolve_* return the value for the stack
# Method delegates called on_* return the Optional[Continue|PauseReason] (None is normal exec)
class Interpreter:
    def __init__(self, func: Callable, in_args=None, in_kwargs=None):
        self.func = func
        instructions = list(dis.get_instructions(self.func))
        self.ops = OpcodeInterpreter(self, instructions)
        self.binds: Dict[str, Any] = {}
        self.state: Dict[str, Any] = {}
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
            if isinstance(a, Object):
                self.binds[name] = OBJECT_PREFIX + a.name
            else:
                self.state[name] = a

    def interpret_instruction(self) -> Continue:
        return self.ops.interpret_instruction()

    def on_return(self, val):
        self.return_val = val
        return Continue(PauseReason.DONE)

    def on_store_fast(self, name, val):
        self.state[name] = val
        if isinstance(val, NonDeterministicSet):
            return Continue(
                kind=PauseReason.YIELD,
                yield_msg=f"NonDeterminism({name})",
                fairness=Fairness.IMMEDIATE,
            )
        return None

    def resolve_call_function(self, func, args):
        if isinstance(func, TagStub):
            raise NotImplementedError()
        else:
            return func(*args)

    def resolve_load_method(self, obj, name):
        method = getattr(obj, name)
        is_bound = False
        if inspect.isbuiltin(method):
            is_bound = True
        if inspect.ismethod(method):
            is_bound = True
        return (is_bound, method)

    def resolve_var_by_name(self, varname: str):
        if varname in self.state:
            return self.state[varname]
        if varname in self.binds:
            ref = self.binds[varname]
            return self._get_from_tree(ref)
        raise LookupError(f"Couldn't find variable {varname}")

    def resolve_var(self, var):
        if isinstance(var, str):
            if var.startswith(OBJECT_PREFIX):
                object = self._get_from_tree(var)
                return object
        return var

    @property
    def pc(self) -> int:
        return self.ops.pc

    @property
    def instructions(self) -> List:
        return self.ops.instructions

    def resolve_getattr(self, base, attr):
        if isinstance(base, str):
            if base.startswith(OBJECT_PREFIX):
                object = self._get_from_tree(base)
                return getattr(object, attr)
        return getattr(base, attr)

    def on_setattr(self, base, attr, val):
        if isinstance(base, str):
            if base.startswith(OBJECT_PREFIX):
                object = self._get_from_tree(base)
                return setattr(object, attr, val)
        setattr(base, attr, val)

    def _get_from_tree(self, base):
        assert self.state_controller is not None
        object_name = base[len(OBJECT_PREFIX) :]
        return self.state_controller.tree[object_name]

    def debug_print(self):
        import pprint

        print("\n\nState:\n")
        pprint.pprint(self.state)
        print("\nInstructions:\n")
        _print_list(self.ops.instructions, self.ops.pc)
        print("\n\n")

    def resolve_global(self, name):
        func_mod = sys.modules[self.func.__module__]
        g = getattr(func_mod, name, None)
        if g is None:
            g = getattr(builtins, name)
        tag = getattr(g, "__timewinder_tag", None)
        if tag is None:
            return g
        return TagStub(tag, self.pc)


@dataclass
class TagStub:
    tag: str
    pc: int


def _print_list(l, highlight):
    highlights = ["   "] * len(l)
    highlights[highlight] = "-> "
    print("\n".join(["%s%s" % x for x in zip(highlights, l)]))

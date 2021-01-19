from telltale.process import Process
from telltale.model import Model
from telltale.statetree import TreeType

from .load_function import get_py_ast
from .statement import interpret_statement

from typing import Any
from typing import Callable
from typing import Dict


class ASTProcessClosure:
    def __init__(self, func: Callable):
        self.func = func
        self.ast = get_py_ast(func)

    def __call__(self, *args, **kwargs):
        return ASTProcess(self, args, kwargs)


class ASTProcess(Process):
    def __init__(self, closure: ASTProcessClosure, in_args, in_kwargs):
        self.ast = closure.ast
        self.func = closure.func
        self._name = self.ast.name
        self.n_steps = len(self.ast.body)
        self.binds: Dict[str, Any] = {}
        self.state: Dict[str, Any] = {}
        self.pc = 0
        if len(in_kwargs) != 0:
            raise NotImplementedError("Need keyword arg binding support")
        argnames = [a.arg for a in self.ast.args.args]
        for name, a in zip(argnames, in_args):
            if isinstance(a, Model):
                self.binds[name] = a.name
            else:
                self.state[name] = a

    @property
    def name(self) -> str:
        return self._name

    def can_execute(self) -> bool:
        pass

    def execute(self, state_controller):
        self.state_controller = state_controller
        interpret_statement(self, self.ast.body[self.pc])
        self.state_controller = None

    def get_state(self) -> TreeType:
        pass

    def set_state(self, state: TreeType):
        pass

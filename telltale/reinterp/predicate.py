from telltale.predicate import Predicate
from telltale.statetree import StateController

from .interpreter import Interpreter


class InterpretedPredicate(Predicate):
    def __init__(self, func, args, kwargs):
        self._name = func.__name__
        self.interp = Interpreter(func, args, kwargs)

    def check(self, sc: StateController) -> bool:
        self.interp.state_controller = sc
        while not self.interp.done:
            self.interp.interpret_instruction()
        self.interp.state_controller = None
        return self.interp.return_val

    @property
    def name(self) -> str:
        return self._name

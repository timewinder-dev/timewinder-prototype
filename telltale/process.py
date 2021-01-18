from abc import ABC
from abc import abstractmethod

from .model import Model

from inspect import isfunction

from typing import List

from telltale.statetree import TreeType


def step(function):
    """Decorator representing an atomic operation between states."""
    if not isfunction(function):
        raise TypeError("Single threads can only be created by decorators on fuctions")

    return Step(function)


class Process(Model, ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def can_execute(self) -> bool:
        pass


class Step:
    def __init__(self, func):
        self.func = func
        self.args = None
        self.kwargs = None
        self.stack = []

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return self

    def _eval(self):
        return self.func(*self.args, **self.kwargs)


class FuncProcess(Process):
    def __init__(self, *args):
        self.steps: List[Step] = args
        self.pc = 0

    def get_state(self) -> TreeType:
        return {"pc": self.pc}

    def set_state(self, state: TreeType) -> None:
        assert isinstance(state, dict)
        self.pc = state["pc"]

    def can_execute(self) -> bool:
        return self.pc < len(self.steps)

    def execute(self):
        assert self.can_execute()
        self.steps[self.pc]._eval()
        self.pc += 1

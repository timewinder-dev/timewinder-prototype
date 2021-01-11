from inspect import isfunction

from typing import List

PCStack = List[int]

InitialStack: PCStack = [0]
FinishedStack: PCStack = []


def step(function):
    """Decorator representing an atomic operation between states."""
    if not isfunction(function):
        raise TypeError("Single threads can only be created by decorators on fuctions")

    return Step(function)


class Algorithm:
    def __init__(self, *args):
        self.steps = args

    def execute_step(self, stack: PCStack) -> List[PCStack]:
        i = stack[0]
        self.steps[i]._eval()
        n = i + 1
        if n >= len(self.steps):
            return [FinishedStack]
        return [[n]]


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

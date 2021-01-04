from inspect import isfunction

from typing import List


def step(function):
    """Decorator representing an atomic operation between states."""
    if not isfunction(function):
        raise TypeError("Single threads can only be created by decorators on fuctions")

    return Step(function)


class Algorithm:
    def __init__(self, *args):
        self.steps = args

    def execute_step(self, i: int):
        self.steps[i]._eval()

    def get_next_states(self, i: int) -> List[int]:
        if i == len(self.steps) - 1:
            return [-1]
        return [i + 1]


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

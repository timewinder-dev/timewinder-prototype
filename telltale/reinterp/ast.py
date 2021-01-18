from telltale.model import Model

import ast

from typing import Any
from typing import Callable
from typing import Dict


class Algorithm:
    def __init__(self, func: Callable, ast: ast.FunctionDef):
        self.func = func
        self.ast = ast
        self.argnames = [a.arg for a in self.ast.args.args]
        self.name = ast.name
        self.n_steps = len(ast.body)

    def __call__(self, *args, **kwargs):
        return BoundAlgorithm(self, args, kwargs)


class BoundAlgorithm:
    def __init__(self, alg: Algorithm, in_args, in_kwargs):
        self.alg = alg
        self.state: Dict[str, Any] = {}
        self.binds: Dict[str, Any] = {}
        if len(in_kwargs) != 0:
            raise NotImplementedError("Need keyword arg binding support")
        for name, a in zip(self.alg.argnames, in_args):
            if isinstance(a, BoundAlgorithm):
                self.binds[name] = a
            elif isinstance(a, Model):
                self.binds[name] = a
            else:
                self.state[name] = a

import ast

from typing import Any
from typing import Callable
from typing import Dict
from typing import Type


def eval_expr(proc, expr: ast.AST) -> Any:
    t = type(expr)
    if t in _expr_dispatch:
        return _expr_dispatch[t](proc, expr)
    raise NotImplementedError(
        f"expressions of type {t} aren't supported yet")


def eval_constant(proc, expr: ast.Constant) -> Any:
    return expr.value


_expr_dispatch: Dict[Type, Callable] = {
    ast.Constant: eval_constant,
}

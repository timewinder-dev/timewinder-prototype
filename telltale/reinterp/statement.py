import ast

from .expr import eval_expr

from typing import Dict
from typing import Callable
from typing import Type
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .process import ASTProcess


def interpret_statement(proc: "ASTProcess", stmt: ast.AST):
    t = type(stmt)
    if t in _stmt_dispatch:
        return _stmt_dispatch[t](proc, stmt)
    raise NotImplementedError(
        f"statements of type {t} aren't supported yet")


def interpret_assign(proc, stmt):
    val = eval_expr(proc, stmt.value)

    _interpret_debug(proc, stmt)
    proc.pc += 1


def interpret_pass(proc, stmt):
    # Just move along
    proc.pc += 1


def _interpret_debug(proc, stmt):
    print("\n***\n", ast.dump(stmt), "\n***")
    raise NotImplementedError()


InterpretSig = Callable[["ASTProcess", ast.AST], None]


_stmt_dispatch: Dict[Type, InterpretSig] = {
    ast.Assign: interpret_assign,
    ast.Pass: interpret_pass,
}

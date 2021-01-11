import ast
import inspect
from .ast import Algorithm


class UncovertableException(BaseException):
    pass


def to_algorithm(func) -> Algorithm:
    py_ast = _get_py_ast(func)
    print(ast.dump(py_ast, indent=2))
    return Algorithm(func, py_ast)


def _get_py_ast(func):
    src_lines, _ = inspect.getsourcelines(func)
    src_lines = _dedent(src_lines)
    src_string = "".join(src_lines)
    py_ast = ast.parse(src_string)
    func_ast = _find_func_definition(py_ast)
    return func_ast


def _dedent(lines):
    if len(lines) == 0:
        raise TypeError("Trying to dedent an empty function")
    out = []
    out.append(lines[0].lstrip())
    indentsize = len(lines[0]) - len(out[0])
    out.extend((line[indentsize:] for line in lines[1:]))
    return out


def _find_func_definition(py_ast: ast.AST) -> ast.FunctionDef:
    if not isinstance(py_ast, ast.Module):
        raise UncovertableException("Not a module")
    if len(py_ast.body) != 1:
        raise UncovertableException("Apparent length of module > 1")
    func = py_ast.body[0]
    if not isinstance(func, ast.FunctionDef):
        raise UncovertableException("First item in body is not a function")
    return func

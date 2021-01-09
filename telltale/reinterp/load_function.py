import ast
import inspect
from .ast import Algorithm


def to_algorithm(func) -> Algorithm:
    src_lines, _ = inspect.getsourcelines(func)
    src_lines = _dedent(src_lines)
    src_string = "".join(src_lines)
    py_ast = ast.parse(src_string)
    print(ast.dump(py_ast, indent=4))

    # return Algorithm([])


def _dedent(lines):
    if len(lines) == 0:
        raise TypeError("Trying to dedent an empty function")
    out = []
    out.append(lines[0].lstrip())
    indentsize = len(lines[0]) - len(out[0])
    out.extend((line[indentsize:] for line in lines[1:]))
    return out

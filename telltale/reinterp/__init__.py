from .process import ASTProcessClosure


def interp(f):
    return ASTProcessClosure(f)

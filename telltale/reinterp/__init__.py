from .process import BytecodeProcessClosure


def interp(f):
    return BytecodeProcessClosure(f)

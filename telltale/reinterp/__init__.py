from .process import BytecodeProcess
from telltale.closure import Closure


def interp(f):
    return Closure(f, BytecodeProcess)

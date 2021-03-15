from .process import BytecodeProcess
from timewinder.closure import Closure


def interp(f):
    return Closure(f, BytecodeProcess)

from typing import Callable
from typing import Optional

from varname import varname

from .model import Model


class ForAll:
    def __init__(self, model: Optional[Model], pred: Callable[[Model], bool]):
        self.modeltype = model
        self.pred = pred
        self.varname = varname()

    def __call__(self, model_states):
        for m in model_states:
            if self.modeltype is not None:
                if not isinstance(m._instance, self.modeltype._cls):
                    continue
            ok = self.pred(m)
            if not ok:
                return ConstraintError(self.varname)
        return None


class ConstraintError(BaseException):
    def __init__(self, name, trace=None):
        self.name = name
        self.trace = trace
        self.state = None

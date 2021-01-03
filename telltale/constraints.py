from typing import Callable
from typing import Optional

from varname import varname

from .model import Model


class ForAll:
    def __init__(self, model: Optional[Model], pred: Callable[[Model], bool]):
        self.model = model
        self.pred = pred
        self.varname = varname()

    def __call__(self, model_states):
        for m in model_states:
            if self.model is not None and isinstance(m._instance, self.model._cls):
                ok = self.pred(m)
                if not ok:
                    return False
        return True

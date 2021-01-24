from abc import ABC
from abc import abstractmethod
from abc import abstractproperty

from typing import Callable
from typing import List
from typing import Optional

from varname import varname

from .model import Model
from .model import ObjectModel


class Predicate(ABC):
    @abstractmethod
    def check(self, models: List[Model]) -> bool:
        pass

    @abstractproperty
    def name(self) -> str:
        pass


class FuncPredicate(Predicate):
    def __init__(self, func, args, kwargs):
        self.args = args
        self.kwargs = kwargs
        self.func = func

    def check(self, models: List[Model]) -> bool:
        # models is ignored, as the binding for a python predicate
        # is already in args/kwargs
        v = self.func(*self.args, **self.kwargs)
        if not isinstance(v, bool):
            raise TypeError("All predicate functions must return a boolean")
        return v


class ForAll(Predicate):
    def __init__(
        self, model: Optional[ObjectModel], pred: Callable[[ObjectModel], bool]
    ):
        self.modeltype = model
        self.pred = pred
        self._name = varname()

    @property
    def name(self) -> str:
        return self._name

    def check(self, models: List[Model]) -> bool:
        for m in models:
            if not isinstance(m, ObjectModel):
                continue
            if self.modeltype is not None:
                if not isinstance(m._instance, self.modeltype._cls):
                    continue
            ok = self.pred(m)
            if not ok:
                return False
        return True


class ConstraintError(BaseException):
    def __init__(self, name, thunk=None):
        self.name = name
        self.thunk = thunk
        self.state = None

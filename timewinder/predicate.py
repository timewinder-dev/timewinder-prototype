from abc import ABC
from abc import abstractmethod
from abc import abstractproperty

from typing import Callable
from typing import List
from typing import TYPE_CHECKING

from varname import varname

from .object import ClassObject
from .closure import Closure

if TYPE_CHECKING:
    from timewinder.statetree import StateController


def predicate(f):
    """Decorator representing a boolean check"""
    return Closure(f, FuncPredicate)


class Predicate(ABC):
    @abstractmethod
    def check(self, sc: "StateController") -> bool:
        pass

    @abstractproperty
    def name(self) -> str:
        pass

    def get_index(self):
        return getattr(self, "index", None)

    def set_index(self, i):
        self.index = i

    def eval_traces(self, traces) -> List[bool]:
        return traces[self.index].trace

    def is_liveness(self) -> bool:
        return False


class FuncPredicate(Predicate):
    def __init__(self, func, args, kwargs):
        self.args = args
        self.kwargs = kwargs
        self.func = func

    def check(self, sc: "StateController") -> bool:
        # sc is ignored, as the binding for a python predicate
        # is already in args/kwargs
        v = self.func(*self.args, **self.kwargs)
        if not isinstance(v, bool):
            raise TypeError("All predicate functions must return a boolean")
        return v

    @property
    def name(self) -> str:
        return self.func.__name__

    def __repr__(self) -> str:
        return self.func.__name__


class ForAll(Predicate):
    def __init__(self, object, pred: Callable[[ClassObject], bool]):
        self.objecttype = object
        self.pred = pred
        self._name = varname()

    @property
    def name(self) -> str:
        return self._name

    def check(self, sc: "StateController") -> bool:
        objects = sc.get_object_list()
        for m in objects:
            if not isinstance(m, ClassObject):
                continue
            if self.objecttype is not None:
                if not isinstance(m._instance, self.objecttype._cls):
                    continue
            ok = self.pred(m)
            if not ok:
                return False
        return True

    def __repr__(self) -> str:
        return f"{self._name}:ForAll({self.pred.__name__})"

from abc import ABC
from abc import abstractmethod
from abc import abstractproperty
from uuid import uuid4
from varname import varname

from timewinder.statetree import TreeType


def object(cls):
    """Decorator wrapping a class representing object state."""

    def wrapper(*args, **kwargs):
        name = varname(raise_exc=False)
        return ClassObject(cls, name, args, kwargs)

    wrapper._cls = cls
    return wrapper


class Object(ABC):
    @abstractproperty
    def name(self) -> str:
        pass

    @abstractmethod
    def get_state(self) -> TreeType:
        pass

    @abstractmethod
    def set_state(self, state: TreeType) -> None:
        """Takes ownership of the given state"""
        pass


class ClassObject(Object):
    """Represents a class as a timewinder object"""

    def __init__(self, cls, name, args, kwargs):
        self._cls = cls
        self._instance = cls(*args, **kwargs)
        if name is not None:
            self._name = name
        else:
            self._name = uuid4().hex

    def get_state(self):
        return self._instance.__dict__

    def set_state(self, state: TreeType) -> None:
        self._instance.__dict__ = state

    @property
    def name(self) -> str:
        return self._name

    def __getattr__(self, key):
        return getattr(self._instance, key)

    def __setattr__(self, key, val):
        if key in ["_instance", "_cls", "_name"]:
            self.__dict__[key] = val
            return
        return setattr(self._instance, key, val)

    def __repr__(self):
        return "%s: %s" % (self._name, self.get_state())

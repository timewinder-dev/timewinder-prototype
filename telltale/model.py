from abc import ABC
from abc import abstractmethod
from abc import abstractproperty
from uuid import uuid4
from varname import varname

from telltale.statetree import TreeType


def model(cls):
    """Decorator wrapping a class representing model state."""

    def wrapper(*args, **kwargs):
        name = varname(raise_exc=False)
        return ObjectModel(cls, name, args, kwargs)

    wrapper._cls = cls
    return wrapper


class Model(ABC):
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


class ObjectModel(Model):
    """Represents a stateful object"""

    def __init__(self, cls, name, args, kwargs):
        self._cls = cls
        self._instance = cls(*args, **kwargs)
        if name is not None:
            self.name = name
        else:
            self.name = uuid4().hex

    def get_state(self):
        return self._instance.__dict__

    def set_state(self, state: TreeType) -> None:
        self._instance.__dict__ = state

    def __getattr__(self, key):
        return getattr(self._instance, key)

    def __setattr__(self, key, val):
        if key in ["_instance", "_cls", "_name"]:
            self.__dict__[key] = val
            return
        return setattr(self._instance, key, val)

    def __repr__(self):
        return "%s: %s" % (self._name, self.get_state())

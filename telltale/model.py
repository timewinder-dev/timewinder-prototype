from typing import List


def model(cls):
    """Decorator wrapping a class representing model state."""

    def wrapper(*args, **kwargs):
        return Model(cls, *args, **kwargs)

    wrapper._cls = cls
    return wrapper


class Model:
    """Represents a stateful object"""

    def __init__(self, cls, *args, **kwargs):
        self._cls = cls
        self._instance = cls(*args, **kwargs)

    def save_state(self) -> List:
        out = list(self._instance.__dict__.items())
        return out

    def restore_state(self, state) -> None:
        for k, v in state:
            self._instance.__dict__[k] = v

    def __getattr__(self, key):
        return getattr(self._instance, key)

    def __setattr__(self, key, val):
        if key in ["_instance", "_cls"]:
            self.__dict__[key] = val
            return
        return setattr(self._instance, key, val)

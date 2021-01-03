from typing import Dict


def model(cls):
    """Decorator wrapping a class representing model state.
    """
    def wrapper(*args, **kwargs):
        return Model(cls, *args, **kwargs)

    return wrapper


class Model:
    """Represents a stateful object"""
    def __init__(self, cls, *args, **kwargs):
        self.instance = cls(*args, **kwargs)

    def save_state(self) -> Dict:
        return self.instance.__dict__

    def restore_state(self, state) -> None:
        for k, v in state:
            self.instance.__dict__[k] = v

    def __getattr__(self, key):
        return getattr(self.instance, key)

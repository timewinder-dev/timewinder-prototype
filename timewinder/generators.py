from typing import Iterable
from typing import Optional


class NonDeterministicSet:
    def __init__(self, s: Iterable):
        self.set = s

    def to_generator(self):
        return (x for x in self.set)


def Set(vals: Iterable) -> NonDeterministicSet:
    return NonDeterministicSet(vals)


def InRange(from_val: int, to_val: Optional[int] = None) -> NonDeterministicSet:
    if to_val is None:
        return Range(from_val + 1)
    return Range(from_val, to_val + 1)


def Range(from_val: int, to_val: Optional[int] = None) -> NonDeterministicSet:
    if to_val is None:
        r = range(from_val)
    else:
        r = range(from_val, to_val)

    return NonDeterministicSet(r)

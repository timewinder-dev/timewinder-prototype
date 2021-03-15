from typing import Iterable
from typing import Generator


def Set(vals: Iterable) -> Generator:
    return (v for v in vals)


def Range(from_val, to_val: int) -> Generator:
    return (i for i in range(from_val, to_val + 1))

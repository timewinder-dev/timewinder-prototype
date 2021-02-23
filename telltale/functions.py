"""
These functions are particular to telltale, and add nondeterminism and other
flow controls.

Executing them should do something worthwhile, but isn't the goal. The tags are
the important part -- looking at the function by tag allows for correct pausing in many situations.
"""

from typing import Iterable


def add_abi_tag(tag: str):
    def wrapper(func):
        func.__telltale_tag = tag
        return func

    return wrapper


@add_abi_tag("await")
def Await(b: bool):
    return b


@add_abi_tag("either")
def Either() -> Iterable[bool]:
    return (x for x in [True, False])
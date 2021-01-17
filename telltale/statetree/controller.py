import itertools
import types

from telltale.model import BaseModel
from .cas import CAS
from .tree import Tree
from .tree import DictTree
from .tree import Hash
from .tree import is_flat_type

from typing import Iterable
from typing import List


class StateController:
    def __init__(self, cas: CAS):
        self.cas = cas
        self.tree = DictTree()
        self.checkouts: List[str] = []

    def mount(self, at: str, model: BaseModel):
        pass

    def commit(self):
        pass

    def restore(self, state_hash: Hash):
        pass


def flatten_to_cas(tree: Tree, cas: CAS) -> Iterable[Hash]:
    non_flats = tree._non_flat_keys()

    # Base case; store and return hash
    if len(non_flats) == 0:
        h = tree.hash()
        cas.put(h, tree)
        yield h
        return

    generators: List[Iterable] = []

    # Create the list of generators to pair with the keys
    # they came from
    for key in non_flats:
        val = tree.get(key)
        if isinstance(val, Tree):
            generators.append(flatten_to_cas(val, cas))
        elif isinstance(val, types.GeneratorType):
            generators.append(val)
        else:
            raise TypeError("Unexpected type while flattening to CAS")

    # Generate the full outer join of the possible values for each key
    for state in itertools.product(*generators):
        # Fill in each key
        for k, v in zip(non_flats, state):
            if not is_flat_type(v) and not isinstance(v, Tree):
                raise TypeError("Generator produced unexpected type flattening to CAS")
            tree.set(k, v)
        # Now, if all the resulting keys are flat, the recursive call
        # hits the base case. If any trees were generated, the recursive
        # call will progress with the newly-flat values filled in and
        # will generate the others.
        yield from flatten_to_cas(tree, cas)
    return

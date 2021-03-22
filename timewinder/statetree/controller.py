import itertools
import copy

from .cas import CAS
from .tree import non_flat_keys
from .tree import Hash
from .tree import hash_flat_tree
from .tree import is_deep_type
from timewinder.generators import NonDeterministicSet

from typing import Dict
from typing import Iterable
from typing import List
from typing import Union
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from timewinder.object import Object


class StateController:
    def __init__(self, cas: CAS):
        self.cas = cas
        self.tree: Dict[str, "Object"] = {}
        self.checkouts: List[str] = []

    def get_object_list(self) -> Iterable["Object"]:
        return self.tree.values()

    def mount(self, at: str, object: "Object"):
        self.tree[at] = object

    def commit(self) -> Iterable[Hash]:
        to_commit = {k: m.get_state() for k, m in self.tree.items()}
        return flatten_to_cas(to_commit, self.cas)

    def restore(self, state_hash: Hash):
        restored = self.cas.restore(state_hash)
        assert isinstance(restored, dict), "StateController only saves dicts"
        for k, v in restored.items():
            self.tree[k].set_state(v)

    def state_to_str(self):
        out = ""
        for k, m in self.tree.items():
            out += f"{k}:\n\t{m}\n"
        return out


def flatten_to_cas(tree: Union[dict, list], cas: CAS) -> Iterable[Hash]:
    non_flats = non_flat_keys(tree)

    # Base case; store and return hash
    if len(non_flats) == 0:
        h = hash_flat_tree(tree)
        cas.put(h, tree)
        yield h
        return

    generators: List[Iterable] = []

    # Create the list of generators to pair with the keys
    # they came from
    for key in non_flats:
        val = tree[key]
        if isinstance(val, dict) or isinstance(val, list):
            generators.append(flatten_to_cas(val, cas))
        elif isinstance(val, NonDeterministicSet):
            generators.append(val.to_generator())
        else:
            raise TypeError("Unexpected type while flattening to CAS")

    # Shallow copy this layer, so we can edit it.
    tree_copy = copy.copy(tree)
    # Generate the full outer join of the possible values for each key
    for state in itertools.product(*generators):
        # Fill in each key
        for k, v in zip(non_flats, state):
            if is_deep_type(v):
                raise TypeError("Generator produced unexpected type flattening to CAS")
            tree_copy[k] = v
        # Now, if all the resulting keys are flat, the recursive call
        # hits the base case. If any trees were generated, the recursive
        # call will progress with the newly-flat values filled in and
        # will generate the others.
        yield from flatten_to_cas(tree_copy, cas)
    return

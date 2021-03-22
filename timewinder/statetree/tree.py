from hashlib import sha256
import msgpack

from timewinder.generators import NonDeterministicSet

from typing import Iterable
from typing import List
from typing import Tuple
from typing import Union


class Hash:
    def __init__(self, b: bytes):
        self.bytes = b

    def hex(self):
        return self.bytes.hex()

    def __repr__(self) -> str:
        return "Hash(%s)" % self.bytes.hex()


TreeType = Union[dict, list]
FlatValueType = Union[Hash, str, int, bool, float, None, bytes]
ValidValueType = Union[FlatValueType, NonDeterministicSet]
TreeableType = Union[ValidValueType, dict, list]


def is_deep_type(v) -> bool:
    if isinstance(v, list):
        return True
    if isinstance(v, dict):
        return True
    if isinstance(v, NonDeterministicSet):
        return True
    return False


def msgpack_ext_default(obj):
    if isinstance(obj, Hash):
        return msgpack.ExtType(1, obj.bytes)
    raise TypeError(f"Unsupported type for serializing tree: {type(obj)}")


_packer = msgpack.Packer(default=msgpack_ext_default)


def _serialize_tree(tree) -> bytes:
    return _packer.pack_map_pairs(sorted(tree.items()))


def _serialize_list(l) -> bytes:
    return _packer.pack(l)


def hash_flat_tree(tree) -> Hash:
    assert len(non_flat_keys(tree)) == 0
    hasher = sha256()
    if isinstance(tree, dict):
        m = _serialize_tree(tree)
    elif isinstance(tree, list):
        m = _serialize_list(tree)
    else:
        raise TypeError("Can only hash dicts or lists")
    hasher.update(m)
    return Hash(hasher.digest())


def non_flat_keys(tree) -> List:
    out = []
    items: Iterable[Tuple]
    if isinstance(tree, list):
        items = enumerate(tree)
    elif isinstance(tree, dict):
        items = tree.items()
    else:
        raise TypeError("Can only check keys of nestable objects")
    for k, v in items:
        if is_deep_type(v):
            out.append(k)
    return out

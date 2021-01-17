from hashlib import sha256
import msgpack

from typing import Iterable
from typing import Generator
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
FlatValueType = Union[str, int, float, bool, None, Hash, bytes]
ValidValueType = Union[FlatValueType, Generator]
TreeableType = Union[ValidValueType, dict, list]


def is_flat_type(v) -> bool:
    return any((isinstance(v, t) for t in FlatValueType.__args__))  # type: ignore


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
        if not is_flat_type(v):
            out.append(k)
    return out

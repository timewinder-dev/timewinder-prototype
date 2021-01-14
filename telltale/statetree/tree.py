from typing import Union
import msgpack

from hashlib import sha256


class Hash(bytes):
    pass


TreeValueType = Union[str, int, float, bool, None, list, dict]


def msgpack_ext_default(obj):
    if isinstance(obj, Hash):
        return msgpack.ExtType(1, bytes(obj))
    if isinstance(obj, Tree):
        return msgpack.ExtType(1, obj.hash())
    raise TypeError(f"Unsupported type for serializing tree: {type(obj)}")


class Tree:
    def __init__(self):
        self._map = {}
        self.packer = msgpack.Packer(default=msgpack_ext_default)

    @classmethod
    def from_dict(cls, d: dict) -> "Tree":
        out = Tree()
        for k, v in d.items():
            if isinstance(v, dict):
                out._map[k] = cls.from_dict(v)
                continue
            out._map[k] = v
        return out

    def set(self, key: str, value: TreeValueType):
        if not isinstance(key, str):
            raise TypeError("All Tree keys must be of type str")
        self._map[key] = value

    def get(self, key: str) -> TreeValueType:
        return self._map[key]

    def __setitem__(self, key: str, value: TreeValueType):
        self.set(key, value)

    def __getitem__(self, key: str):
        return self.get(key)

    def hash(self) -> bytes:
        m = sha256(self.serialize())
        return m.digest()

    def serialize(self) -> bytes:
        self._check_value_types()
        self.packer.pack_map_pairs(sorted(self._map.items()))
        return self.packer.bytes()

    def _check_value_types(self):
        for v in self._map.values():
            if not is_supported_type(v):
                raise TypeError(f"Uncommitable value type in this Tree: {type(v)}")

    def is_flat(self) -> bool:
        for v in self._map.values():
            if not is_supported_type(v):
                return False
            if isinstance(v, Tree):
                return False
        return True


_valid_types = [str, int, float, bool, type(None), list, Hash, Tree]


def is_supported_type(v) -> bool:
    return any((isinstance(v, t) for t in _valid_types))

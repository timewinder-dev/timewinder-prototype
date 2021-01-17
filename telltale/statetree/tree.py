from abc import abstractmethod
from copy import deepcopy
from hashlib import sha256
import msgpack
import types

from typing import Iterable
from typing import Generator
from typing import List
from typing import Dict
from typing import Tuple
from typing import Union


class Hash:
    def __init__(self, b: bytes):
        self.bytes = b

    def hex(self):
        return self.bytes.hex()

    def __repr__(self) -> str:
        return "Hash(%s)" % self.bytes.hex()


_flat_types = [str, int, float, bool, type(None), Hash, bytes]

TreeValueType = Union[str, int, float, bool, None, Hash, bytes]
ValidValueType = Union[TreeValueType, "Tree", Generator]
TreeableType = Union[ValidValueType, dict, list]


def is_flat_type(v) -> bool:
    return any((isinstance(v, t) for t in _flat_types))


def msgpack_ext_default(obj):
    if isinstance(obj, Hash):
        return msgpack.ExtType(1, obj.bytes)
    if isinstance(obj, Tree):
        return msgpack.ExtType(1, obj.hash().bytes)
    raise TypeError(f"Unsupported type for serializing tree: {type(obj)}")


_packer = msgpack.Packer(default=msgpack_ext_default)


def treeify_value(val: TreeableType):
    if is_flat_type(val):
        return val
    if isinstance(val, list):
        return ListTree(val)
    if isinstance(val, dict):
        return DictTree(val)
    if isinstance(val, types.GeneratorType):
        return val
    raise TypeError(f"Type {type(val)} is not yet supported in statetree")


class Tree:
    def hash(self) -> Hash:
        m = sha256(self.serialize())
        return Hash(m.digest())

    @abstractmethod
    def serialize(self) -> bytes:
        pass

    @abstractmethod
    def items(self) -> Iterable[Tuple]:
        pass

    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def set(self, key, value: ValidValueType):
        pass

    def _non_flat_keys(self) -> List:
        out = []
        for k, v in self.items():
            if not is_flat_type(v):
                out.append(k)
        return out

    def is_flat(self) -> bool:
        return len(self._non_flat_keys()) == 0

    @abstractmethod
    def _mem_save(self):
        pass


class DictTree(Tree):
    def __init__(self, initial_map: Dict[str, ValidValueType] = None):
        self._map: Dict[str, ValidValueType] = {}
        if initial_map is not None:
            for k, v in initial_map.items():
                self.set(k, v)

    def set(self, key: str, value: ValidValueType):
        if not isinstance(key, str):
            raise TypeError("All DictTree keys must be of type str")
        val = treeify_value(value)
        self._map[key] = val

    def get(self, key: str):
        return self._map[key]

    def __setitem__(self, key: str, value: ValidValueType):
        self.set(key, value)

    def __getitem__(self, key: str):
        return self.get(key)

    def items(self) -> Iterable[Tuple]:
        return self._map.items()

    def serialize(self) -> bytes:
        assert self.is_flat()
        return _packer.pack_map_pairs(sorted(self._map.items()))

    def _mem_save(self):
        return deepcopy(self._map)


class ListTree(Tree):
    def __init__(self, initial_list: List[ValidValueType] = None):
        self._list: List[ValidValueType] = []
        if initial_list is not None:
            for v in initial_list:
                self.append(v)

    def set(self, key: int, value: ValidValueType):
        if not isinstance(key, int):
            raise TypeError("All ListTree keys must be of type int")
        val = treeify_value(value)
        self._list[key] = val

    def get(self, key: int):
        return self._list[key]

    def __setitem__(self, key: int, value: ValidValueType):
        self.set(key, value)

    def __getitem__(self, key: int):
        return self.get(key)

    def append(self, item):
        self._list.append(0)
        self.set(-1, item)

    def items(self) -> Iterable[Tuple]:
        return enumerate(self._list)

    def serialize(self) -> bytes:
        assert self.is_flat()
        return _packer.pack(self._list)

    def _mem_save(self):
        return deepcopy(self._list)

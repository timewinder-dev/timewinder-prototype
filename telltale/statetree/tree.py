from typing import Union
from typing import NewType
from typing import List
import struct

from hashlib import sha256

from operator import attrgetter

Hash = NewType("Hash", int)
JSONValue = Union[str, int, float, bool, None]
JSONStruct = Union[dict, list, tuple]
JSONType = Union[JSONValue, JSONStruct]


class Tree:
    prefix = b"\x01"

    def __init__(self, nodes: List["Node"] = None):
        if nodes is None:
            self.nodes = []
        else:
            self.nodes = nodes

    def _sort_nodes(self):
        self.nodes.sort(key=attrgetter("key"))

    def append(self, node: "Node"):
        self.nodes.append(node)

    def clone(self) -> "Tree":
        return Tree([n.clone() for n in self.nodes])

    def hash(self) -> bytes:
        self._sort_nodes()
        hashes = (n.hash() for n in self.nodes)
        m = sha256(self.prefix)
        for h in hashes:
            m.update(h)
        return m.digest()

    def to_obj(self):
        out = {}
        for n in self.nodes:
            v = n.value
            if isinstance(v, Tree):
                out[n.key] = v.to_obj()
            else:
                out[n.key] = v
        return out


class ListTree(Tree):
    prefix = b"\x02"

    def clone(self) -> "ListTree":
        return ListTree([n.clone() for n in self.nodes])

    def _sort_nodes(self):
        self.nodes.sort(key=lambda n: int(n.key))

    def to_obj(self):
        self._sort_nodes()
        out = []
        for n in self.nodes:
            v = n.value
            if isinstance(v, Tree):
                out.append(v.to_obj())
            else:
                out.append(v)
        return out


class Node:
    def __init__(self, key: str, value: Union[JSONValue, Tree]):
        self.key = key
        self.value = value

    def clone(self) -> "Node":
        if isinstance(self.value, Tree):
            return Node(self.key, self.value.clone())
        return Node(self.key, self.value)

    def hash(self) -> bytes:
        m = sha256()
        m.update(self.key.encode("utf8"))
        m.update(b"\x00")
        m.update(self.value_type_byte())
        m.update(self._value_bytes())
        return m.digest()

    def _value_bytes(self) -> bytes:
        if isinstance(self.value, str):
            return self.value.encode("utf8")
        elif isinstance(self.value, int):
            # Python can represent bigints, which might be worth another type.
            # For now, we'll assume int64.
            return struct.pack("<q", self.value)
        elif isinstance(self.value, float):
            return struct.pack("<d", self.value)
        elif isinstance(self.value, bool):
            return b""
        elif self.value is None:
            return b""
        elif isinstance(self.value, Tree):
            return self.value.hash()

    def value_type_byte(self) -> bytes:
        if isinstance(self.value, str):
            return b"\x00"
        elif isinstance(self.value, int):
            return b"\x01"
        elif isinstance(self.value, float):
            return b"\x02"
        elif isinstance(self.value, bool):
            if self.value:
                return b"\x03"
            return b"\x83"
        elif self.value is None:
            return b"\x04"
        elif isinstance(self.value, Tree):
            return b"\xff"
        assert False, "Unreachable"

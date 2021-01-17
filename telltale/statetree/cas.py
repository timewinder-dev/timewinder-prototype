import copy

from abc import ABC
from abc import abstractmethod

from typing import Dict
from typing import Iterable

from .tree import TreeType
from .tree import Hash
from .tree import non_flat_keys


class CAS(ABC):
    @abstractmethod
    def put(self, sha: Hash, data: TreeType):
        pass

    @abstractmethod
    def get(self, sha: Hash) -> TreeType:
        pass

    @abstractmethod
    def debug_print(self):
        pass

    @abstractmethod
    def size(self) -> int:
        pass

    def restore(self, sha: Hash) -> TreeType:
        data = self.get(sha)
        items: Iterable
        if isinstance(data, list):
            items = enumerate(data)
        elif isinstance(data, dict):
            items = data.items()
        else:
            raise TypeError("Returning a non-TreeType data?")
        for k, v in items:
            if isinstance(v, Hash):
                data[k] = self.restore(v)
        return data


class MemoryCAS(CAS):
    def __init__(self):
        self.store: Dict[bytes, TreeType] = {}

    def put(self, sha: Hash, data: TreeType):
        assert len(non_flat_keys(data)) == 0
        self.store[sha.bytes] = copy.copy(data)

    def get(self, sha: Hash) -> TreeType:
        return copy.copy(self.store[sha.bytes])

    def debug_print(self):
        import pprint

        for k, v in self.store.items():
            print("")
            print(f"{k.hex()}")
            print("=" * 10)
            pprint.pprint(v)

    def size(self) -> int:
        return len(self.store)

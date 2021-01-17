from abc import ABC
from abc import abstractmethod

from typing import Dict

from .tree import Hash
from .tree import Tree
from .tree import treeify_value


class CAS(ABC):
    @abstractmethod
    def put(self, sha: Hash, data: Tree):
        pass

    @abstractmethod
    def get(self, sha: Hash) -> Tree:
        pass


class MemoryCAS(CAS):
    def __init__(self):
        self.store: Dict[bytes, Tree] = {}

    def put(self, sha: Hash, data: Tree):
        assert data.is_flat()
        self.store[sha.bytes] = data._mem_save()

    def get(self, sha: Hash) -> Tree:
        return treeify_value(self.store[sha.bytes])

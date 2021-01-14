from abc import ABC
from abc import abstractmethod

from typing import Dict

from .tree import Tree


class CAS(ABC):
    @abstractmethod
    def put(self, sha: bytes, data: Tree):
        pass

    @abstractmethod
    def get(self, sha: bytes) -> Tree:
        pass


class MemoryCAS(CAS):
    def __init__(self):
        self.store: Dict[bytes, Tree] = {}

    def put(self, sha: bytes, data: Tree):
        self.store[sha] = data

    def get(self, sha: bytes) -> Tree:
        return self.store[sha]

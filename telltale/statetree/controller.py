from typing import Dict
from typing import List
from telltale.model import BaseModel

from .cas import CAS
from .tree import Tree
from .tree import Hash


class StateController:
    def __init__(self, cas: CAS):
        self.cas = cas
        self.mounts: Dict[str, BaseModel] = {}
        self.tree = Tree()
        self.checkouts: List[str] = []

    def commit(self):
        pass

    def restore(self, state_hash: Hash):
        pass

    def checkout(self, path: str):
        pass

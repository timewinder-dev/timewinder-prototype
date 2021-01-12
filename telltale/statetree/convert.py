from .tree import Tree
from .tree import ListTree
from .tree import Node

_supported_types = [int, bool, float, str, list, dict]


def _is_supported_type(x) -> bool:
    if x is None:
        return True
    for t in _supported_types:
        if isinstance(x, t):
            return True
    return False


def dict_to_tree(d: dict) -> Tree:
    tree = Tree()
    for k, v in d.items():
        tree.append(Node(k, _tree_value(v)))
    return tree


def _tree_value(v):
    if not _is_supported_type(v):
        raise TypeError("Supported types are JSON-ish or Telltale supertypes")
    if isinstance(v, list):
        return list_to_tree(v)
    elif isinstance(v, dict):
        return dict_to_tree(v)
    else:
        return v


def list_to_tree(vs: list) -> Tree:
    tree = ListTree()
    for i, v in enumerate(vs):
        k = str(i)
        tree.append(Node(k, _tree_value(v)))
    return tree

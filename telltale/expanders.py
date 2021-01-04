from copy import deepcopy
from abc import abstractmethod
from abc import ABC
import itertools

from typing import Iterable
from typing import Dict
from typing import List
from typing import Tuple

from .model import Model


class BaseExpander(ABC):
    @abstractmethod
    def make_states(self, initial_state: Dict, key: str) -> Iterable[Dict]:
        pass


class Set(BaseExpander):
    def __init__(self, vals):
        self.vals = vals

    def make_states(self, initial_state: Dict, key: str) -> Iterable[Dict]:
        out = []
        for v in self.vals:
            new = deepcopy(initial_state)
            new[key] = v
            out.append(new)
        return out


def expand_states(initial_states: List[Model]) -> Iterable:
    expanded: List[List[Tuple]]
    expanded = [expand_model_states(m) for m in initial_states]
    return ([sorted(list(t.items())) for t in x] for x in itertools.product(*expanded))


def expand_model_states(m: Model):
    init = m.state_dict()
    expand_queue: Iterable[Dict] = [init]
    for k, v in init.items():
        if isinstance(v, BaseExpander):
            expand_queue = itertools.chain.from_iterable(
                [v.make_states(s, k) for s in expand_queue]
            )
    return expand_queue

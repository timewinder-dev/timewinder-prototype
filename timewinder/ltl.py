from abc import ABC
from abc import abstractmethod

from .predicate import Predicate

from typing import List
from typing import Union

from dataclasses import dataclass
from copy import copy


@dataclass
class TTrace:
    trace: List[bool]

    def clone(self):
        return TTrace(trace=copy(self.trace))

    def __len__(self) -> int:
        return len(self.trace)

    def append(self, b: bool):
        self.trace.append(b)


def eventually(l: List[bool]) -> List[bool]:
    if len(l) == 0:
        return []
    return [any(l)] + eventually(l[1:])


def always(l: List[bool]) -> List[bool]:
    if len(l) == 0:
        return []
    return [all(l)] + always(l[1:])


def inverse(l: List[bool]) -> List[bool]:
    return [not x for x in l]


def implies(p, q: List[bool]) -> List[bool]:
    assert len(p) == len(q)
    if len(p) == 0:
        return []
    v = True
    if p[0] and not q[0]:
        v = False
    return [v] + implies(p[1:], q[1:])


def leads_to(p, q: List[bool]) -> List[bool]:
    return always(implies(p, eventually(q)))


class LTLOp(ABC):
    def __init__(self, pred: "LTLExpression"):
        self.pred = pred

    def to_ltl_tree(self):
        """Make a JSON-able representation of LTLOps"""
        if isinstance(self.pred, Predicate):
            v = self.pred.get_index()
        else:
            v = self.pred.to_ltl_tree()
        return {self._tree_key: v}

    def get_predicates(self) -> List[Predicate]:
        if isinstance(self.pred, Predicate):
            return [self.pred]
        return self.pred.get_predicates()

    @abstractmethod
    def eval_traces(self, traces: List[TTrace]) -> List[bool]:
        pass

    @abstractmethod
    def is_liveness(self) -> bool:
        pass


class LTLBinOp(LTLOp):
    def __init__(self, pred: "LTLExpression", pred2: "LTLExpression"):
        self.pred = pred
        self.pred2 = pred2

    def to_ltl_tree(self):
        if isinstance(self.pred, Predicate):
            v = self.pred.get_index()
        else:
            v = self.pred.to_ltl_tree()
        if isinstance(self.pred2, Predicate):
            w = self.pred2.get_index()
        else:
            w = self.pred2.to_ltl_tree()
        return {self._tree_key: [v, w]}

    def get_predicates(self) -> List[Predicate]:
        if isinstance(self.pred, Predicate):
            a = [self.pred]
        else:
            a = self.pred.get_predicates()

        if isinstance(self.pred2, Predicate):
            b = [self.pred2]
        else:
            b = self.pred2.get_predicates()

        return a + b


LTLExpression = Union[LTLOp, Predicate]


class Eventually(LTLOp):
    _tree_key = "eventually"

    def eval_traces(self, traces: List[TTrace]) -> List[bool]:
        return eventually(self.pred.eval_traces(traces))

    def is_liveness(self) -> bool:
        return True

    def __repr__(self) -> str:
        return "<>(%s)" % str(self.pred)


class Always(LTLOp):
    _tree_key = "always"

    def eval_traces(self, traces: List[TTrace]) -> List[bool]:
        return always(self.pred.eval_traces(traces))

    def is_liveness(self) -> bool:
        return self.pred.is_liveness()

    def __repr__(self) -> str:
        return "[](%s)" % str(self.pred)


class Not(LTLOp):
    _tree_key = "inverse"

    def eval_traces(self, traces: List[TTrace]) -> List[bool]:
        return inverse(self.pred.eval_traces(traces))

    def is_liveness(self) -> bool:
        return self.pred.is_liveness()

    def __repr__(self) -> str:
        return "!(%s)" % str(self.pred)


class LeadsTo(LTLBinOp):
    _tree_key = "leads_to"

    def eval_traces(self, traces: List[TTrace]) -> List[bool]:
        return leads_to(self.pred.eval_traces(traces), self.pred2.eval_traces(traces))

    def is_liveness(self) -> bool:
        return True

    def __repr__(self) -> str:
        return "(%s) ~> (%s)" % (str(self.pred), str(self.pred2))

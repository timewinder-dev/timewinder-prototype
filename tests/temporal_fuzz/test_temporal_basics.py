from hypothesis import given, assume, settings
from hypothesis.strategies import lists, booleans

from typing import List

TTrace = List[bool]


def to_bool(l: TTrace) -> bool:
    return l[0]


def always_bool(l: TTrace) -> bool:
    return all(l)


def always(l: TTrace) -> TTrace:
    if len(l) == 0:
        return []
    return [all(l)] + always(l[1:])


def eventually_bool(l: TTrace) -> bool:
    return any(l)


def eventually(l: TTrace) -> TTrace:
    if len(l) == 0:
        return []
    return [any(l)] + eventually(l[1:])


def eventuallyAlways_bool(l: TTrace) -> bool:
    if len(l) == 0:
        return True
    if len(l) == 1:
        return l[0]
    if l[0] is True:
        return always_bool(l[1:]) or eventuallyAlways_bool(l[1:])
    else:
        return eventuallyAlways_bool(l[1:])


def alwaysEventually_bool(l: TTrace) -> bool:
    if len(l) == 0:
        return False
    if len(l) == 1:
        return l[0]
    if l[0] is True:
        return alwaysEventually_bool(l[1:])
    else:
        return eventually_bool(l[1:]) and alwaysEventually_bool(l[1:])


def inverse(l: TTrace) -> TTrace:
    return [not x for x in l]


def leadsTo_bool(p, q: TTrace) -> bool:
    assert len(p) == len(q)
    if len(p) == 0:
        return True
    if p[0] is True:
        if q[0] is True:
            return leadsTo_bool(p[1:], q[1:])
        else:
            return eventually_bool(q[1:]) and leadsTo_bool(p[1:], q[1:])
    else:
        return leadsTo_bool(p[1:], q[1:])


def leadsTo(p, q: TTrace) -> TTrace:
    pass


@given(lists(booleans()))
def test_always(l):
    assume(len(l) > 0)
    assert to_bool(always(l)) == always_bool(l)
    if always_bool(l):
        assert eventuallyAlways_bool(l)
        assert to_bool(eventually(always(l))) == always_bool(l)


@given(lists(booleans()))
def test_eventually(l):
    assume(len(l) > 0)
    assert to_bool(eventually(l)) == eventually_bool(l)
    assert to_bool(always(eventually(l))) == alwaysEventually_bool(l)
    if alwaysEventually_bool(l):
        assert eventually_bool(l)


@given(lists(booleans()))
@settings(max_examples=2000)
def test_eventually_not_always_not(p):
    assert eventually(p) == inverse(always(inverse(p)))


@given(lists(booleans()))
@settings(max_examples=2000)
def test_leads_to_equivalence(p):
    assume(len(p) > 0)
    assert leadsTo_bool(inverse(p), p) == to_bool(always(eventually(p)))

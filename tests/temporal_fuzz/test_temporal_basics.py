from hypothesis import given, assume, settings
from hypothesis.strategies import lists, booleans

from typing import List


def always(l: List[bool]) -> bool:
    return all(l)


def eventually(l: List[bool]) -> bool:
    return any(l)


def eventuallyAlways(l: List[bool]) -> bool:
    if len(l) == 0:
        return True
    if len(l) == 1:
        return l[0]
    if l[0] is True:
        return always(l[1:]) or eventuallyAlways(l[1:])
    else:
        return eventuallyAlways(l[1:])


def alwaysEventually(l: List[bool]) -> bool:
    if len(l) == 0:
        return False
    if len(l) == 1:
        return l[0]
    if l[0] is True:
        return alwaysEventually(l[1:])
    else:
        return eventually(l[1:]) and alwaysEventually(l[1:])


def inverse(l: List[bool]) -> List[bool]:
    return [not x for x in l]


def leadsTo(p, q: List[bool]) -> bool:
    assert len(p) == len(q)
    if len(p) == 0:
        return True
    if p[0] is True:
        if q[0] is True:
            return leadsTo(p[1:], q[1:])
        else:
            return eventually(q[1:]) and leadsTo(p[1:], q[1:])
    else:
        return leadsTo(p[1:], q[1:])


@given(lists(booleans()))
def test_always(l):
    assume(len(l) > 0)
    if always(l):
        assert eventuallyAlways(l)


@given(lists(booleans()))
def test_eventually(l):
    assume(len(l) > 0)
    if alwaysEventually(l):
        assert eventually(l)


@given(lists(booleans()))
@settings(max_examples=2000)
def test_eventually_not_always_not(p):
    assume(len(p) > 0)
    assert eventually(p) == (not always(inverse(p)))


@given(lists(booleans()))
@settings(max_examples=2000)
def test_leads_to_equivalence(p):
    assume(len(p) > 0)
    assert leadsTo(inverse(p), p) == alwaysEventually(p)

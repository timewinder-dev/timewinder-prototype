import pytest
from hypothesis import given, assume, settings
from hypothesis.strategies import lists, booleans, integers, tuples
from random import randint

from timewinder.ltl import eventually
from timewinder.ltl import always
from timewinder.ltl import inverse
from timewinder.ltl import leads_to

from typing import List

TTrace = List[bool]


def generate_trace(length: int) -> TTrace:
    out = []
    for i in range(length):
        x = randint(0, 1)
        if x == 0:
            out.append(True)
        else:
            out.append(False)
    return out


def to_bool(l: TTrace) -> bool:
    return l[0]


def always_bool(l: TTrace) -> bool:
    return all(l)


def eventually_bool(l: TTrace) -> bool:
    return any(l)


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
@settings(max_examples=500)
def test_eventually_not_always_not(p):
    assert eventually(p) == inverse(always(inverse(p)))


@given(lists(booleans()))
@settings(max_examples=500)
def test_leads_to_equivalence(p):
    assume(len(p) > 0)
    assert leadsTo_bool(inverse(p), p) == to_bool(always(eventually(p)))
    assert leads_to(inverse(p), p) == always(eventually(p))


def matching_lists(min, max=20):
    return integers(min_value=min, max_value=max).flatmap(
        lambda n: tuples(
            lists(booleans(), min_size=n, max_size=n),
            lists(booleans(), min_size=n, max_size=n),
        )
    )


@given(matching_lists(1))
@settings(max_examples=500)
def test_leads_to_def(ls):
    p, q = ls
    assert to_bool(leads_to(p, q)) == leadsTo_bool(p, q)


@pytest.mark.benchmark(group="ltl_microbenchmark")
def test_leads_to_bm(benchmark):
    p = generate_trace(100)
    q = generate_trace(100)
    benchmark(leads_to, p, q)

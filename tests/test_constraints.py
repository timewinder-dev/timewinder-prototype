import timewinder
import timewinder.statetree

from tests.test_helpers import A


def test_forall():
    a = A()

    sc = timewinder.statetree.StateController(timewinder.statetree.MemoryCAS())
    sc.mount("a", a)

    ok = timewinder.ForAll(A, lambda m: m.foo == "a")
    assert ok.check(sc)

    fail = timewinder.ForAll(A, lambda m: m.foo == "b")
    assert not fail.check(sc)

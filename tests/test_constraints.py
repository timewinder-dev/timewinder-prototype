import telltale
import telltale.statetree

from tests.test_helpers import A


def test_forall():
    a = A()

    sc = telltale.statetree.StateController(telltale.statetree.MemoryCAS())
    sc.mount("a", a)

    ok = telltale.ForAll(A, lambda m: m.foo == "a")
    assert ok.check(sc)

    fail = telltale.ForAll(A, lambda m: m.foo == "b")
    assert not fail.check(sc)

import telltale

from tests.test_helpers import A


def test_forall():
    a = A()

    ok = telltale.ForAll(A, lambda m: m.foo == "a")
    assert ok([a])

    fail = telltale.ForAll(A, lambda m: m.foo == "b")
    assert not fail([a])

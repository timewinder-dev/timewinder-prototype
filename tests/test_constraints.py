import telltale

from tests.test_helpers import A
from telltale.constraints import ConstraintError


def test_forall():
    a = A()

    ok = telltale.ForAll(A, lambda m: m.foo == "a")
    assert ok([a]) is None

    fail = telltale.ForAll(A, lambda m: m.foo == "b")
    assert isinstance(fail([a]), ConstraintError)

import telltale
import pytest
from telltale.evaluation import state_hash

from tests.test_helpers import A


def test_savestate():
    @telltale.model
    class DoIt:
        def __init__(self):
            self.foo = "b"

        def doit(self):
            self.foo = "bar"

    a = DoIt()
    s = a.save_state()
    a.doit()
    assert a.foo == "bar"
    assert state_hash(s) != state_hash(a.save_state())
    a.restore_state(s)
    assert a.foo == "b"
    assert state_hash(s) == state_hash(a.save_state())


def test_simple_eval():
    @telltale.thread
    def t(m):
        if m.foo == "a":
            m.foo = "b"
            return
        m.foo = "a"

    a = A()

    ev = telltale.Evaluator(
        models=[a],
        threads=[t(a)],
    )

    ev.evaluate(steps=4)


def test_multi_eval():
    @telltale.thread
    def t(m):
        m.foo = "b"
        x(m)

    @telltale.thread
    def x(m):
        assert m.foo == "b"
        m.foo = "a"

    a = A()

    ev = telltale.Evaluator(
        models=[a],
        threads=[t(a)],
    )

    ev.evaluate(steps=4)
    assert ev.stats.states == 2


def test_subcall_onestate():
    @telltale.thread
    def t(m):
        m.foo = "b"
        x(m)

    # Intentionally not a thread -- so t calls it in one step
    def x(m):
        assert m.foo == "b"
        m.foo = "a"

    a = A()

    ev = telltale.Evaluator(
        models=[a],
        threads=[t(a)],
    )

    ev.evaluate(steps=4)
    assert ev.stats.states == 1


def test_assert_fail():
    @telltale.thread
    def t(m):
        m.foo = "b"

    @telltale.thread
    def x(m):
        assert m.foo == "b"

    a = A()

    ev = telltale.Evaluator(
        models=[a],
        threads=[t(a), x(a)],
    )

    with pytest.raises(AssertionError):
        ev.evaluate(steps=4)

import telltale
import pytest

from tests.test_helpers import A


def test_simple_eval():
    @telltale.step
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
    @telltale.step
    def t(m):
        m.foo = "b"

    @telltale.step
    def x(m):
        assert m.foo == "b"
        m.foo = "a"

    a = A()

    ev = telltale.Evaluator(
        models=[a],
        threads=[telltale.Algorithm(t(a), x(a))],
    )

    ev.evaluate(steps=4)
    ev._print_state_space()
    assert ev.stats.cas_objects == 4


def test_subcall_onestate():
    @telltale.step
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
    assert ev.stats.cas_objects == 2


def test_assert_fail():
    @telltale.step
    def t(m):
        m.foo = "b"

    @telltale.step
    def x(m):
        assert m.foo == "b"

    a = A()

    ev = telltale.Evaluator(
        models=[a],
        threads=[t(a), x(a)],
    )

    with pytest.raises(AssertionError):
        ev.evaluate(steps=4)

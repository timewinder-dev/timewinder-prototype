import telltale  # noqa: F401
from telltale.evaluation import state_hash


def test_savestate():
    @telltale.model
    class A:
        def __init__(self):
            self.foo = "b"

        def doit(self):
            self.foo = "bar"

    a = A()
    s = a.save_state()
    a.doit()
    assert a.foo == "bar"
    assert state_hash(s) != state_hash(a.save_state())
    a.restore_state(s)
    assert a.foo == "b"
    assert state_hash(s) == state_hash(a.save_state())


def test_simple_eval():
    @telltale.model
    class A:
        def __init__(self):
            self.foo = "b"

        def __repr__(self):
            return "A: " + self.foo

    @telltale.thread
    def t(m):
        if m.foo == "b":
            m.foo = "a"
            return
        m.foo = "b"

    a = A()

    ev = telltale.Evaluator(
        models=[a],
        threads=[t(a)],
    )

    ev.evaluate(steps=4)

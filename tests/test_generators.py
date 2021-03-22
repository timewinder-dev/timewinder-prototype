import timewinder
from timewinder.statetree import StateController
from timewinder.statetree import MemoryCAS
import timewinder.generators as gens


def test_cross_product_id():
    @timewinder.object
    class A:
        def __init__(self):
            self.a = 1
            self.b = 2

    s = StateController(MemoryCAS())
    s.mount("a", A())
    all_states = s.commit()
    states = list(all_states)
    assert len(states) == 1


def test_cross_product_one():
    @timewinder.object
    class A:
        def __init__(self):
            self.a = 1
            self.b = gens.Set(["a", "b", "c"])

    s = StateController(MemoryCAS())
    s.mount("a", A())
    all_states = s.commit()
    states = list(all_states)
    assert len(states) == 3


def test_cross_product_a():
    @timewinder.object
    class A:
        def __init__(self):
            self.a = gens.InRange(0, 2)
            self.b = gens.InRange(0, 3)

    s = StateController(MemoryCAS())
    s.mount("a", A())
    all_states = s.commit()
    states = list(all_states)
    assert len(states) == 12


def test_cross_product_b():
    @timewinder.object
    class A:
        def __init__(self):
            self.a = gens.InRange(0, 2)
            self.b = gens.InRange(0, 3)

    s = StateController(MemoryCAS())
    s.mount("a", A())
    s.mount("b", A())
    all_states = s.commit()
    states = list(all_states)
    assert len(states) == 144

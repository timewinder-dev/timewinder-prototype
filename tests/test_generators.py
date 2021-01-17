import telltale
from telltale.statetree import StateController
from telltale.statetree import MemoryCAS
import telltale.generators as gens


def test_cross_product_id():
    @telltale.model
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
    @telltale.model
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
    @telltale.model
    class A:
        def __init__(self):
            self.a = gens.Range(0, 3)
            self.b = gens.Range(0, 4)

    s = StateController(MemoryCAS())
    s.mount("a", A())
    all_states = s.commit()
    states = list(all_states)
    assert len(states) == 12


def test_cross_product_b():
    @telltale.model
    class A:
        def __init__(self):
            self.a = gens.Range(0, 3)
            self.b = gens.Range(0, 4)

    s = StateController(MemoryCAS())
    s.mount("a", A())
    s.mount("b", A())
    all_states = s.commit()
    states = list(all_states)
    assert len(states) == 144

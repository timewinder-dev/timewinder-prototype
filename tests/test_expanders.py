import telltale
import telltale.expanders as expanders


def test_cross_product_id():
    @telltale.model
    class A:
        def __init__(self):
            self.a = 1
            self.b = 2

    a = A()
    all_states = expanders.expand_states([a])
    states = list(all_states)
    assert len(states) == 1


def test_cross_product_one():
    @telltale.model
    class A:
        def __init__(self):
            self.a = 1
            self.b = expanders.Set(range(3))

    a = A()
    all_states = expanders.expand_states([a])
    states = list(all_states)
    assert len(states) == 3


def test_cross_product_a():
    @telltale.model
    class A:
        def __init__(self):
            self.a = expanders.Set(range(3))
            self.b = expanders.Set(range(4))

    a = A()
    all_states = expanders.expand_states([a])
    states = list(all_states)
    assert len(states) == 12


def test_cross_product_b():
    @telltale.model
    class A:
        def __init__(self):
            self.a = expanders.Set(range(3))
            self.b = expanders.Set(range(4))

    a = A()
    b = A()
    all_states = expanders.expand_states([a, b])
    states = list(all_states)
    assert len(states) == 144

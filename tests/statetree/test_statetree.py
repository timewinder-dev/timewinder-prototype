import pytest

import telltale.statetree.tree as tree
import telltale.statetree.cas as cas
import telltale.statetree.controller as controller


example = {
    "name": "a",
    "vals": [1, 2, 3],
    "more": {
        "foo": 2.5,
        "bar": 2,
        "ok": True,
        "nope": None,
    },
}


def test_convert_tree():
    t = tree.treeify_value(example)
    with pytest.raises(AssertionError):
        h = t.hash()

    c = cas.MemoryCAS()
    g = list(controller.flatten_to_cas(t, c))
    assert len(g) == 1
    h = g[0]
    assert h.hex() == "76d66a06f234fb456f08e439d87f9b254c9ffe3839866b1c9420397caf1e85ff"

    assert len(c.store) == 3


def test_treeify_microbenchmark(benchmark):
    benchmark(tree.treeify_value, example)


def test_flatten_to_cas_microbenchmark(benchmark):
    t = tree.treeify_value(example)
    c = cas.MemoryCAS()

    benchmark(controller.flatten_to_cas, t, c)


def test_flatten_generator(benchmark):
    generator = {
        "a": (i for i in range(5)),
        "b": (i for i in range(4)),
    }

    t = tree.treeify_value(generator)
    c = cas.MemoryCAS()

    shas = list(benchmark(controller.flatten_to_cas, t, c))
    assert len(shas) == 20
    assert len(c.store) == 20

    restore = c.store.get(shas[-1].bytes)
    assert restore["a"] == 4
    assert restore["b"] == 3


def test_nested_generator(benchmark):
    generator = {
        "a": {
            "internal": (i for i in range(5)),
        },
        "b": (i for i in range(4)),
    }

    t = tree.treeify_value(generator)
    c = cas.MemoryCAS()

    shas = list(benchmark(controller.flatten_to_cas, t, c))
    assert len(shas) == 20
    assert len(c.store) == 25

    restore = c.store.get(shas[-1].bytes)
    assert c.get(restore["a"])["internal"] == 4
    assert restore["b"] == 3


def test_subtree_reuse():
    generator = {
        "a": {
            "internal": (i for i in range(5)),
        },
        "b": {
            "internal": (i for i in range(4)),
        },
    }

    t = tree.treeify_value(generator)
    c = cas.MemoryCAS()

    shas = list(controller.flatten_to_cas(t, c))
    assert len(shas) == 20
    assert len(c.store) == 25
    # The full number of computed shas ought to be 29; but the
    # overlapping 4 internals are reused

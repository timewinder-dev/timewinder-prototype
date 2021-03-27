import timewinder.statetree.cas as cas
import timewinder.statetree.controller as controller
import timewinder.generators as gen


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
    c = cas.MemoryCAS()
    g = list(controller.flatten_to_cas(example, c))
    assert len(g) == 1
    h = g[0]
    assert h.hex() == "76d66a06f234fb456f08e439d87f9b254c9ffe3839866b1c9420397caf1e85ff"

    assert len(c.store) == 3


def test_flatten_to_cas_microbenchmark(benchmark):
    c = cas.MemoryCAS()
    benchmark(controller.flatten_to_cas, example, c)


def test_flatten_generator(benchmark):
    generator = {
        "a": gen.Range(5),
        "b": gen.Range(4),
    }

    c = cas.MemoryCAS()

    shas = list(benchmark(controller.flatten_to_cas, generator, c))
    assert len(shas) == 20
    assert len(c.store) == 20

    restore = c.store.get(shas[-1].bytes)
    assert restore["a"] == 4
    assert restore["b"] == 3


def test_nested_generator(benchmark):
    generator = {
        "a": {
            "internal": gen.Range(5),
        },
        "b": gen.Range(4),
    }

    c = cas.MemoryCAS()

    shas = list(benchmark(controller.flatten_to_cas, generator, c))
    assert len(shas) == 20
    assert len(c.store) == 25

    restore = c.store.get(shas[-1].bytes)
    assert c.get(restore["a"])["internal"] == 4
    assert restore["b"] == 3


def test_subtree_reuse():
    generator = {
        "a": {
            "internal": gen.Range(5),
        },
        "b": {
            "internal": gen.Range(4),
        },
    }

    c = cas.MemoryCAS()

    shas = list(controller.flatten_to_cas(generator, c))
    assert len(shas) == 20
    assert len(c.store) == 25
    # The full number of computed shas ought to be 29; but the
    # overlapping 4 internals are reused


def test_generator_of_generator():
    g = {
        "a": gen.Set((sorted(x) for x in [[1, 3, 2]] * 4)),
    }
    c = cas.MemoryCAS()

    shas = list(controller.flatten_to_cas(g, c))
    assert len(shas) == 4
    assert len(set(shas)) == 1


def test_generator_of_generators():
    g = {
        "a": gen.Set((sorted(x) for x in (y for y in [[1, 3, 2]] * 4))),
    }
    c = cas.MemoryCAS()

    shas = list(controller.flatten_to_cas(g, c))
    assert len(shas) == 4
    assert len(set(shas)) == 1

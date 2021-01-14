import telltale.statetree.tree as tree


example = {
    "name": "A",
    "vals": [1, 2, 3],
    "more": {
        "foo": 2.5,
        "bar": 2,
        "ok": True,
        "nope": None,
    },
}


def test_convert_tree():
    t = tree.Tree.from_dict(example)
    h = t.hash()
    assert h.hex() == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_convert_tree_benchmark(benchmark):
    benchmark(tree.Tree.from_dict, example)

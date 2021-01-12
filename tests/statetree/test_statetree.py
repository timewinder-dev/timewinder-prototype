import telltale.statetree.convert as convert
import json


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
    t = convert.dict_to_tree(example)
    h = t.hash()
    assert h.hex() == "0336563ac838da7fcdbb12495539fa07378c1236e8a069397b7a2fec4085cc87"

    exstr = json.dumps(example, sort_keys=True)
    assert exstr == json.dumps(t.to_obj(), sort_keys=True)

    a = convert.list_to_tree([1, 2, 3])
    b = convert.dict_to_tree({"0": 1, "1": 2, "2": 3})

    assert a.hash() != b.hash()


def test_convert_tree_benchmark(benchmark):
    benchmark(convert.dict_to_tree, example)


def test_hash_tree_benchmark(benchmark):
    t = convert.dict_to_tree(example)
    benchmark(t.hash)

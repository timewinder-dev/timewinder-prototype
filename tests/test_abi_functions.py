import timewinder
from timewinder.functions import ThreadID
from dataclasses import dataclass


def test_abi_thread_idx():
    @timewinder.object
    @dataclass
    class Result:
        result: int

    @timewinder.process
    def get_thread_id(res):
        res.result = ThreadID()

    r = Result(-1)

    ev = timewinder.Evaluator(
        objects=[r],
        threads=[get_thread_id(r)],
    )
    ev.evaluate()
    assert r.result == 0

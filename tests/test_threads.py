import timewinder

from tests.test_helpers import A


def test_run_deep_calls():
    object = A()

    @timewinder.step
    def a(state, m):
        print("in a")
        m.foo = "b"

    @timewinder.step
    def b(state, m):
        m.foo = "c"

    @timewinder.step
    def c(state, m):
        m.foo = "end1"

    @timewinder.step
    def d(state, m):
        m.foo = "end2"

    alg = timewinder.FuncProcess(
        a(object),
        b(object),
        c(object),
        d(object),
    )

    ev = timewinder.Evaluator(
        objects=[object],
        threads=[alg],
    )

    ev.evaluate()
    assert ev.stats.states == 5
    ev._print_state_space()

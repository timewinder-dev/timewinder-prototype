import telltale

from tests.test_helpers import A


def test_run_deep_calls():
    model = A()

    @telltale.step
    def a(state, m):
        print("in a")
        m.foo = "b"

    @telltale.step
    def b(state, m):
        m.foo = "c"

    @telltale.step
    def c(state, m):
        m.foo = "end1"

    @telltale.step
    def d(state, m):
        m.foo = "end2"

    alg = telltale.FuncProcess(
        a(model),
        b(model),
        c(model),
        d(model),
    )

    ev = telltale.Evaluator(
        models=[model],
        threads=[alg],
    )

    ev.evaluate()
    assert ev.stats.states == 5
    ev._print_state_space()

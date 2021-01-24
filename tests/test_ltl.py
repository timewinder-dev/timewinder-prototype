import telltale.ltl as ltl
from tests.test_helpers import MockPredicate


mocks = [MockPredicate(x) for x in range(10)]


def test_eventually():
    ev = ltl.Eventually(mocks[0])
    trace = ltl.TTrace(trace=[False, True, False])
    result = ev.eval_traces([trace])
    assert result == [True, True, False]


def test_always():
    ev = ltl.Always(mocks[0])
    trace = ltl.TTrace(trace=[False, True, False])
    result = ev.eval_traces([trace])
    assert result == [False, False, False]

    trace = ltl.TTrace(trace=[False, True, True])
    result = ev.eval_traces([trace])
    assert result == [False, True, True]


def test_leads_to():
    ev = ltl.LeadsTo(mocks[0], mocks[1])
    trace = ltl.TTrace(trace=[False, True, False])
    trace2 = ltl.TTrace(trace=[False, False, True])

    result = ev.eval_traces([trace, trace2])
    assert result == [True, True, True]


def test_eventually_always():
    ev = ltl.Eventually(ltl.Always(mocks[0]))

    trace = ltl.TTrace(trace=[False, True, False])
    result = ev.eval_traces([trace])
    assert result == [False, False, False]

    trace = ltl.TTrace(trace=[False, True, True])
    result = ev.eval_traces([trace])
    assert result == [True, True, True]


def test_ltl_tree():
    ev = ltl.Eventually(ltl.Always(mocks[7]))
    assert ev.to_ltl_tree() == {"eventually": {"always": 7}}

    ev = ltl.Eventually(ltl.LeadsTo(mocks[6], mocks[5]))
    assert ev.to_ltl_tree() == {"eventually": {"leads_to": [6, 5]}}

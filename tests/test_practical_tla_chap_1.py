import timewinder
import pytest

from timewinder.generators import Set
from timewinder.evaluation import ConstraintError


def test_overdraft_1():
    @timewinder.model
    class Account:
        def __init__(self, name):
            self.name = name
            self.acc = 5

    alice = Account("alice")
    bob = Account("bob")

    @timewinder.step
    def withdraw(state, sender, amount):
        sender.acc = sender.acc - amount

    @timewinder.step
    def deposit(state, reciever, amount):
        reciever.acc = reciever.acc + amount

    alg = timewinder.FuncProcess(
        withdraw(alice, 3),
        deposit(bob, 3),
    )

    no_overdrafts = timewinder.ForAll(Account, lambda a: a.acc >= 0)

    ev = timewinder.Evaluator(
        models=[alice, bob],
        threads=[alg],
        specs=[no_overdrafts],
    )
    ev.evaluate()
    ev._print_state_space()
    assert ev.stats.states == 3


def test_overdraft_initial_conditions():
    @timewinder.model
    class Account:
        def __init__(self, name):
            self.name = name
            self.acc = 5

    alice = Account("alice")
    bob = Account("bob")

    @timewinder.step
    def withdraw(state, sender):
        sender.acc = sender.acc - state["amt"]

    @timewinder.step
    def deposit(state, reciever):
        reciever.acc = reciever.acc + state["amt"]

    alg = timewinder.FuncProcess(
        withdraw(alice),
        deposit(bob),
        state={
            "amt": Set(range(1, 7)),
        },
    )

    no_overdrafts = timewinder.ForAll(Account, lambda a: a.acc >= 0)

    ev = timewinder.Evaluator(
        models=[alice, bob],
        threads=[alg],
        specs=[no_overdrafts],
    )

    got_error = False
    try:
        ev.evaluate()
    except ConstraintError as e:
        got_error = True
        print(e.name)
        print(e.thunk)

    assert got_error
    assert ev.stats.states == 12


def test_multiple_processes():
    @timewinder.model
    class Account:
        def __init__(self, name):
            self.name = name
            self.acc = 5

    alice = Account("alice")
    bob = Account("bob")

    @timewinder.step
    def withdraw(state, sender):
        sender.acc = sender.acc - state["amt"]

    @timewinder.step
    def deposit(state, reciever):
        reciever.acc = reciever.acc + state["amt"]

    def alg():
        return timewinder.FuncProcess(
            withdraw(alice),
            deposit(bob),
            state={"amt": Set(range(1, 6))},
        )

    no_overdrafts = timewinder.ForAll(Account, lambda a: a.acc >= 0)

    ev = timewinder.Evaluator(
        models=[alice, bob],
        threads=[alg(), alg()],
        specs=[no_overdrafts],
    )

    got_error = False
    try:
        ev.evaluate()
    except ConstraintError as e:
        got_error = True
        print(e.name, " failed")
        ev.replay_thunk(e.thunk)

    assert got_error
    assert ev.stats.states == 89


def test_multiple_processes_if():
    @timewinder.model
    class Account:
        def __init__(self, name):
            self.name = name
            self.acc = 5

    alice = Account("alice")
    bob = Account("bob")

    @timewinder.step
    def withdraw(state, sender):
        sender.acc = sender.acc - state["amt"]

    @timewinder.step
    def deposit(state, reciever):
        reciever.acc = reciever.acc + state["amt"]

    @timewinder.step
    def check_funds(state, sender):
        if state["amt"] > sender.acc:
            raise timewinder.StopProcess()

    def alg():
        return timewinder.FuncProcess(
            check_funds(alice),
            withdraw(alice),
            deposit(bob),
            state={"amt": Set(range(1, 6))},
        )

    no_overdrafts = timewinder.ForAll(Account, lambda a: a.acc >= 0)

    ev = timewinder.Evaluator(
        models=[alice, bob],
        threads=[alg(), alg()],
        specs=[no_overdrafts],
    )

    got_error = False
    try:
        ev.evaluate(steps=10)
    except ConstraintError as e:
        got_error = True
        print(e.name, " failed")
        ev.replay_thunk(e.thunk)

    assert got_error
    assert ev.stats.states == 295


@pytest.mark.benchmark(group="practical_tla_1")
def test_check_and_withdraw(benchmark):
    @timewinder.model
    class Account:
        def __init__(self, name):
            self.name = name
            self.acc = 5

    @timewinder.step
    def deposit(state, reciever):
        reciever.acc = reciever.acc + state["amt"]

    @timewinder.step
    def check_and_withdraw(state, sender):
        if state["amt"] > sender.acc:
            raise timewinder.StopProcess()
        else:
            sender.acc = sender.acc - state["amt"]

    no_overdrafts = timewinder.ForAll(Account, lambda a: a.acc >= 0)

    def reset_and_eval():
        alice = Account("alice")
        bob = Account("bob")

        def alg():
            return timewinder.FuncProcess(
                check_and_withdraw(alice),
                deposit(bob),
                state={"amt": Set(range(1, 6))},
            )

        ev = timewinder.Evaluator(
            models=[alice, bob],
            threads=[alg(), alg()],
            specs=[no_overdrafts],
        )
        ev.evaluate(steps=10)
        return ev.stats

    stats = benchmark(reset_and_eval)

    assert stats.states == 225

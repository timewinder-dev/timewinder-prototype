import telltale

from telltale.generators import Set
from telltale.constraints import ConstraintError


def test_overdraft_1():
    @telltale.model
    class Account:
        def __init__(self, name):
            self.name = name
            self.acc = 5

    alice = Account("alice")
    bob = Account("bob")

    @telltale.step
    def withdraw(state, sender, amount):
        sender.acc = sender.acc - amount

    @telltale.step
    def deposit(state, reciever, amount):
        reciever.acc = reciever.acc + amount

    alg = telltale.FuncProcess(
        withdraw(alice, 3),
        deposit(bob, 3),
    )

    no_overdrafts = telltale.ForAll(Account, lambda a: a.acc >= 0)

    ev = telltale.Evaluator(
        models=[alice, bob],
        threads=[alg],
        specs=[no_overdrafts],
    )
    ev.evaluate()
    ev._print_state_space()
    assert ev.stats.states == 3


def test_overdraft_initial_conditions():
    @telltale.model
    class Account:
        def __init__(self, name):
            self.name = name
            self.acc = 5

    alice = Account("alice")
    bob = Account("bob")

    @telltale.step
    def withdraw(state, sender):
        sender.acc = sender.acc - state["amt"]

    @telltale.step
    def deposit(state, reciever):
        reciever.acc = reciever.acc + state["amt"]

    alg = telltale.FuncProcess(
        withdraw(alice),
        deposit(bob),
        state={
            "amt": Set(range(1, 7)),
        },
    )

    no_overdrafts = telltale.ForAll(Account, lambda a: a.acc >= 0)

    ev = telltale.Evaluator(
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
    @telltale.model
    class Account:
        def __init__(self, name):
            self.name = name
            self.acc = 5

    alice = Account("alice")
    bob = Account("bob")

    @telltale.step
    def withdraw(state, sender):
        sender.acc = sender.acc - state["amt"]

    @telltale.step
    def deposit(state, reciever):
        reciever.acc = reciever.acc + state["amt"]

    def alg():
        return telltale.FuncProcess(
            withdraw(alice),
            deposit(bob),
            state={"amt": Set(range(1, 5))},
        )

    no_overdrafts = telltale.ForAll(Account, lambda a: a.acc >= 0)

    ev = telltale.Evaluator(
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
    assert ev.stats.states == 71

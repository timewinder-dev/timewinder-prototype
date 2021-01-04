import telltale

from telltale.expanders import Set
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
    def withdraw(sender, amount):
        sender.acc = sender.acc - amount

    @telltale.step
    def deposit(reciever, amount):
        reciever.acc = reciever.acc + amount

    alg = telltale.Algorithm(
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
    assert ev.stats.states == 3


def test_overdraft_initial_conditions():
    @telltale.model
    class Account:
        def __init__(self, name):
            self.name = name
            self.acc = 5

    @telltale.model
    class ThreadState:
        def __init__(self):
            self.amt = Set(range(1, 7))

    alice = Account("alice")
    bob = Account("bob")
    s = ThreadState()

    @telltale.step
    def withdraw(sender, state):
        sender.acc = sender.acc - state.amt

    @telltale.step
    def deposit(reciever, state):
        reciever.acc = reciever.acc + state.amt

    alg = telltale.Algorithm(
        withdraw(alice, s),
        deposit(bob, s),
    )

    no_overdrafts = telltale.ForAll(Account, lambda a: a.acc >= 0)

    ev = telltale.Evaluator(
        models=[alice, bob, s],
        threads=[alg],
        specs=[no_overdrafts],
    )

    got_error = False
    try:
        ev.evaluate()
    except ConstraintError as e:
        got_error = True
        print(e.name)
        print(e.trace)
        print(e.state)

    assert got_error
    assert ev.stats.states == 12

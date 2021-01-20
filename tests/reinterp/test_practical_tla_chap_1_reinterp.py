import telltale
import pytest

from telltale.reinterp import interp
from telltale.generators import Set
from telltale.constraints import ConstraintError


@telltale.model
class Account:
    def __init__(self, name, amt):
        self.name = name
        self.acc = amt


def test_overdraft_1():
    alice = Account("alice", 5)
    bob = Account("bob", 5)

    @interp
    def withdraw(sender, reciever, amount):
        sender.acc = sender.acc - amount
        yield "deposit"
        reciever.acc = reciever.acc + amount

    no_overdrafts = telltale.ForAll(Account, lambda a: a.acc >= 0)

    ev = telltale.Evaluator(
        models=[alice, bob],
        threads=[withdraw(alice, bob, 3)],
        specs=[no_overdrafts],
    )
    ev.evaluate()
    ev._print_state_space()
    assert ev.stats.states == 3


def test_overdraft_initial_conditions():
    alice = Account("alice", 5)
    bob = Account("bob", 5)

    @interp
    def withdraw(sender, reciever, amount):
        sender.acc = sender.acc - amount
        yield "deposit"
        reciever.acc = reciever.acc + amount

    no_overdrafts = telltale.ForAll(Account, lambda a: a.acc >= 0)

    ev = telltale.Evaluator(
        models=[alice, bob],
        threads=[withdraw(alice, bob, Set(range(1, 7)))],
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


@pytest.mark.benchmark(group="practical_tla_1")
def test_check_and_withdraw_reinterp(benchmark):
    @interp
    def check_and_withdraw(sender, reciever, amt):
        if amt <= sender.acc:
            sender.acc = sender.acc - amt
            yield "deposit"
            reciever.acc = reciever.acc + amt

    no_overdrafts = telltale.ForAll(Account, lambda a: a.acc >= 0)

    def reset_and_eval():
        alice = Account("alice", 5)
        bob = Account("bob", 5)

        ev = telltale.Evaluator(
            models=[alice, bob],
            threads=[
                check_and_withdraw(alice, bob, Set(range(1, 6))),
                check_and_withdraw(alice, bob, Set(range(1, 6))),
            ],
            specs=[no_overdrafts],
        )
        ev.evaluate(steps=10)
        return ev.stats

    stats = benchmark(reset_and_eval)

    assert stats.states == 225

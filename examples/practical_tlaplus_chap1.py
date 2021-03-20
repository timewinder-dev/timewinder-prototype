import timewinder
from timewinder.generators import Set


@timewinder.model
class Account:
    def __init__(self, name, amt):
        self.name = name
        self.acc = amt


@timewinder.process
def withdraw(sender, reciever, amount):
    sender.acc = sender.acc - amount
    yield "deposit"
    reciever.acc = reciever.acc + amount


# This process checks that the amount to transfer isn't more
# than the account sender has before continuing.
@timewinder.process
def check_and_withdraw(sender, reciever, amt):
    if amt <= sender.acc:
        sender.acc = sender.acc - amt
        yield "deposit"
        reciever.acc = reciever.acc + amt


alice = Account("alice", 5)
bob = Account("bob", 5)


no_overdrafts = timewinder.ForAll(Account, lambda a: a.acc >= 0)


ev = timewinder.Evaluator(
    models=[alice, bob],
    # Alternately, only have one thread do a withdrawal of too much
    # money, and it should fail.
    #
    # threads=[withdraw(alice, bob, 6)],
    threads=[
        check_and_withdraw(alice, bob, Set(range(1, 7))),
        check_and_withdraw(alice, bob, Set(range(1, 7))),
    ],
    specs=[no_overdrafts],
)
err = None
try:
    ev.evaluate()
except timewinder.ConstraintError as e:
    err = e

if err is None:
    print(ev.stats)
else:
    print("\n" + err.name + "\n")
    ev.replay_thunk(err.thunk)

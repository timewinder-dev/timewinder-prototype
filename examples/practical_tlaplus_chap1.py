import timewinder
from timewinder.generators import Set

# This model intends to check the correctness of bank
# accounts and moving money between them, with different
# constraints.
#
# This is adapted from Chapter 1 of _Practical_TLA+_ by
# Hillel Wayne


# Start by defining an account.
@timewinder.object
class Account:
    def __init__(self, name, amt):
        self.name = name
        self.acc = amt


# The simplest transfer withdraws from the sender, and then,
# sometime later, puts that amount in the recieving account.
@timewinder.process
def withdraw(sender, reciever, amount):
    sender.acc = sender.acc - amount
    yield "deposit"
    reciever.acc = reciever.acc + amount


# This is a more intelligent transfer, that checks that the
# amount to transfer isn't more than the account sender has
# in their account before continuing.
@timewinder.process
def check_and_withdraw(sender, reciever, amt):
    if amt <= sender.acc:
        sender.acc = sender.acc - amt
        yield "deposit"
        reciever.acc = reciever.acc + amt


# Instantiate our example account objects
alice = Account("alice", 5)
bob = Account("bob", 5)


# Create a predicate that says, at every stage, all Account
# objects must carry positive balances.
no_overdrafts = timewinder.ForAll(Account, lambda a: a.acc >= 0)


# Run the evaluator.
ev = timewinder.Evaluator(
    # Pass our two objects
    objects=[alice, bob],
    # Declare the predicates we want to check.
    specs=[no_overdrafts],
    # Only have one thread do a withdrawal of too much
    # money, and it should fail.
    #
    threads=[withdraw(alice, bob, 6)],
    # Alternately, run two threads, both withdrawing from Alice and depositing
    # to Bob's account. The `Set` function is a generator that will
    # try every transfer amount from 1 to 5, as per Python's `range`
    # builtin.
    #
    # This should fail, as both must complete and will in some cases
    # (both amounts at 1) but will fail if too much is transferred.
    #
    # threads=[
    #    check_and_withdraw(alice, bob, Set(range(1, 6))),
    #    check_and_withdraw(alice, bob, Set(range(1, 6))),
    # ],
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

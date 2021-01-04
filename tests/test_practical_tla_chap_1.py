import telltale


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
    print(ev.stats)

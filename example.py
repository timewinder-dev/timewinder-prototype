from telltale import model
from telltale import thread
from telltale import Evaluator


@model
class Account(object):
    def __init__(self, name):
        self.money = 5
        self.name = name


@thread
def transfer(acc_from, acc_to, amount):
    withdraw(acc_from, amount)
    deposit(acc_to, amount)


@thread
def withdraw(acc_from, amount):
    acc_from.money -= amount


@thread
def deposit(acc_to, amount):
    acc_to.money += amount


def noOverdrafts(models):
    for m in models:
        assert m.money >= 0


alice = Account("alice")
bob = Account("bob")


ev = Evaluator(
    models=[alice, bob],
    threads=[transfer(alice, bob, 3)],
    specs=[noOverdrafts([alice, bob])],
)

ev.evaluate()

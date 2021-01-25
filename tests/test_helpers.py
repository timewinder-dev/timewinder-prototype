import telltale
from telltale.predicate import Predicate


@telltale.model
class A:
    def __init__(self):
        self.foo = "a"

    def __repr__(self):
        return "A: " + self.foo


class MockPredicate(Predicate):
    def __init__(self, index):
        self.index = index

    def check(self, sc) -> bool:
        raise NotImplementedError()

    def name(self) -> str:
        return "Mock"

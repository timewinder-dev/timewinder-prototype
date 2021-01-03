import telltale


@telltale.model
class A:
    def __init__(self):
        self.foo = "a"

    def __repr__(self):
        return "A: " + self.foo

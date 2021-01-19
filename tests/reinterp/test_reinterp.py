from telltale.reinterp.process import ASTProcessClosure


def Call(x, y):
    pass
    with x in y as foo:
        Call(foo)
    ll = [f for f in y]
    return ll


def test_pass_func():
    def f(x):
        pass

    a = ASTProcessClosure(f)
    proc = a(2)
    proc.execute(None)


def test_dumb_assign():
    def f(x):
        x = 2
        return x + x

    a = ASTProcessClosure(f)
    proc = a(2)
    proc.execute(None)


def test_interesting_assign():
    def f(acc):
        acc["foo"] = 2
        # comment
        x = 2
        y = set()
        x = x - 1
        return y

    a = ASTProcessClosure(f)
    proc = a({"foo": 1})
    proc.execute(None)


def test_yield():
    def f(acc):
        yield "Step 1"
        if acc <= 2:
            yield "Step 2"
        return 3

    a = ASTProcessClosure(f)
    proc = a(1)
    proc.execute(None)
    assert proc.name == "Step 1"
    proc.execute(None)
    assert proc.name == "Step 2"
    proc.execute(None)

from telltale.reinterp.process import ASTProcessClosure


def Call(x):
    pass


def f(acc):
    acc["foo"] = 2
    # comment
    x = 2
    y = set()
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
        a = 2

    a = ASTProcessClosure(f)
    proc = a(2)
    proc.execute(None)

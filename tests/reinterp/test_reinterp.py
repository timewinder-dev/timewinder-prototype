import telltale.reinterp as reinterp


def Call(x):
    pass


def f(acc):
    acc["foo"] = 2
    # comment
    with x in y as foo:
        Call(foo)
    ll = [f for f in y]
    return ll


def test_init():

    reinterp.to_algorithm(f)
    # do some checks
    # reinterp.interp(steps[0])

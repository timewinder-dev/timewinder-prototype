def thread(function):
    """Decorator representing an atomic operation between states.
    """
    return Thread(function)


class Thread:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        yield
        return self.func(*args, **kwargs)

    def _evaluate(self)

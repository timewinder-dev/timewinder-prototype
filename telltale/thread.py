def thread(function):
    """Decorator representing an atomic operation between states.
    """
    return Thread(function)


_is_executing = False


def _set_execution(b: bool):
    global _is_executing
    _is_executing = b


class Thread:
    def __init__(self, func):
        self.func = func
        self.args = None
        self.kwargs = None

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        global _is_executing
        if _is_executing:
            self._eval()
        else:
            return self

    def _eval(self):
        yield self.func(*self.args, **self.kwargs)

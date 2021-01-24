class Closure:
    def __init__(self, func, cls):
        self.cls = cls
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.cls(self.func, args, kwargs)

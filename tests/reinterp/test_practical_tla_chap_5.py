import timewinder


@timewinder.model
class Queue:
    def __init__(self, transmit=4):
        self.queue = []
        self.to_transmit = transmit


@timewinder.predicate
def bounded_queue(q, size):
    return len(q.queue) <= size


def test_processes():
    q = Queue()

    @timewinder.process
    def writer(q):
        while True:
            yield "Write"
            q.queue.append("msg")

    @timewinder.process
    def reader(q):
        while True:
            yield "Read"
            _ = q.queue[0]
            q.queue = q.queue[1:]

    ev = timewinder.Evaluator(
        models=[q],
        threads=[writer(q), reader(q)],
        specs=[bounded_queue(q, 2)],
    )

    got_error = False
    try:
        ev.evaluate()
    except timewinder.ProcessException as e:
        got_error = True
        print(e)

    assert got_error


def test_emulate_await_p1():
    q = Queue()

    @timewinder.process
    def writer(q):
        while True:
            yield "Write"
            q.queue.append("msg")

    @timewinder.process
    def reader(q):
        while True:
            yield "Read"
            if len(q.queue) == 0:
                continue
            _ = q.queue[0]
            q.queue = q.queue[1:]

    ev = timewinder.Evaluator(
        models=[q],
        threads=[writer(q), reader(q)],
        specs=[bounded_queue(q, 2)],
    )

    got_error = False
    try:
        ev.evaluate()
    except timewinder.ConstraintError as e:
        got_error = True
        assert e.name.find("bounded_queue") >= 0
        print(e.name)
        ev.replay_thunk(e.thunk)

    assert got_error


def test_emulate_await_p2():
    q = Queue()

    @timewinder.process
    def writer(q):
        while True:
            yield "Write"
            q.queue.append("msg")
            while len(q.queue) >= 2:
                yield "Waiting"

    @timewinder.process
    def reader(q):
        while True:
            yield "Read"
            if len(q.queue) == 0:
                continue
            _ = q.queue[0]
            q.queue = q.queue[1:]

    ev = timewinder.Evaluator(
        models=[q],
        threads=[writer(q), reader(q)],
        specs=[bounded_queue(q, 2)],
    )

    try:
        ev.evaluate(steps=100)
    except timewinder.ConstraintError as e:
        print(e.name)
        ev.replay_thunk(e.thunk)
        assert False

    assert ev.stats.states == 13


def test_transmit_extension():
    q = Queue(40)
    max_queue_length = 7

    @timewinder.process
    def writer(q, max):
        while q.to_transmit != 0:
            yield "Write"
            q.queue.append("msg")
            q.to_transmit -= 1
            while len(q.queue) >= max:
                yield "Waiting"

    @timewinder.process
    def reader(q):
        while q.to_transmit > 0 or len(q.queue) > 0:
            yield "Read"
            if len(q.queue) == 0:
                continue
            _ = q.queue[0]
            q.queue = q.queue[1:]

    ev = timewinder.Evaluator(
        models=[q],
        threads=[writer(q, max_queue_length), reader(q)],
        specs=[
            bounded_queue(q, max_queue_length),
        ],
    )

    try:
        ev.evaluate(steps=None)
    except timewinder.ConstraintError as e:
        print(e.name)
        ev.replay_thunk(e.thunk)
        raise e

    assert ev.stats.states == 555

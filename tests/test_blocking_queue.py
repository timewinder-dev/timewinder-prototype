import timewinder
from timewinder.generators import Set

@timewinder.object
class BoundedQueue:
    def __init__(self, max_length):
        self._max = max_length
        self.queue = []

    def is_full(self):
        return len(self.queue) >= self._max

    def is_empty(self):
        return len(self.queue) == 0


# This is a hack, as accessing internal thread state is not
# yet implemented.
@timewinder.object
class ThreadCanRun:
    def __init__(self, n_producers, n_consumers):
        self.status = [True] * (n_producers + n_consumers)
        self.n_producers = n_producers
        self.n_consumers = n_consumers

    def notify(self, i):
        self.status[i] = True

    def sleeping(self):
        return [i for i, x in enumerate(self.status) if x is False]


@timewinder.process
def producer(queue, running, id):
    while True:
        if not running.status[id]:
            yield "paused"
            continue
        while not queue.is_full():
            queue.queue.append(4)  # 4 represents arbitrary data
        sleeping = running.sleeping()
        running.status[id] = False
        if len(sleeping) == 0:
            continue
        wake_id = Set(sleeping)
        yield "waking"
        print(wake_id)
        running.notify(wake_id)


@timewinder.process
def consumer(queue, running, id):
    while True:
        if not running.status[id]:
            yield "paused"
            continue
        while not queue.is_empty():
            queue.queue.pop()
        sleeping = running.sleeping()
        running.status[id] = False
        if len(sleeping) == 0:
            continue
        wake_id = Set(sleeping)
        yield "waking"
        running.notify(wake_id)


def bounded_queue_example(n_producers, n_consumers, queue_size):
    n_threads = n_producers + n_consumers
    runnable = ThreadCanRun(n_producers, n_consumers)
    bqueue = BoundedQueue(queue_size)

    threads = []
    for i in range(n_threads):
        if i < n_producers:
            threads.append(producer(bqueue, runnable, i))
        else:
            threads.append(consumer(bqueue, runnable, i))

    no_deadlocks = timewinder.ForAll(ThreadCanRun, lambda c: any(c.status))

    return timewinder.Evaluator(
        objects=[runnable, bqueue],
        specs=[no_deadlocks],
        threads=threads,
    )


def test_bounded_queue_ok():
    ev = bounded_queue_example(1,1,1)
    err = None
    try:
        env.evaluate(steps=20)
    except timewinder.ConstraintError as e:
        err = e

    assert err is None
    print(ev.stats)


def test_bounded_queue_fail():
    ev = bounded_queue_example(2,1,1)
    err = None
    try:
        ev.evaluate(steps=50)
    except timewinder.ConstraintError as e:
        err = e

    assert err is not None
    print("\n" + err.name + "\n")
    ev.replay_thunk(err.thunk)

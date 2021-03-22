import timewinder
from timewinder.generators import Set

# These are the variables we'd like to modify to test
# bigger models.
PRODUCERS = 2
CONSUMERS = 1
QUEUE_SIZE = 1


@timewinder.object
class BoundedQueue:
    def __init__(self, max_length):
        self._max = max_length
        self.queue = []

    def is_full(self):
        return len(self.queue) >= self._max

    def is_empty(self):
        return len(self.queue) == 0


# This emulates cond_wait
@timewinder.object
class CondWait:
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
        if queue.is_full():
            running.status[id] = False
            continue
        queue.queue.append(4)  # 4 represents arbitrary data

        sleeping = running.sleeping()
        if len(sleeping) != 0:
            wake_id = Set(sleeping)
            running.notify(wake_id)


@timewinder.process
def consumer(queue, running, id):
    while True:
        if not running.status[id]:
            yield "paused"
            continue
        if queue.is_empty():
            running.status[id] = False
            continue

        queue.queue.pop()

        sleeping = running.sleeping()
        if len(sleeping) != 0:
            wake_id = Set(sleeping)
            running.notify(wake_id)


THREADS = PRODUCERS + CONSUMERS
runnable = CondWait(PRODUCERS, CONSUMERS)
bqueue = BoundedQueue(QUEUE_SIZE)


threads = []
for i in range(THREADS):
    if i < PRODUCERS:
        threads.append(producer(bqueue, runnable, i))
    else:
        threads.append(consumer(bqueue, runnable, i))


no_deadlocks = timewinder.ForAll(CondWait, lambda c: any(c.status))


ev = timewinder.Evaluator(
    objects=[runnable, bqueue],
    specs=[no_deadlocks],
    threads=threads,
)


err = None
try:
    ev.evaluate(steps=None)
except timewinder.ConstraintError as e:
    err = e


if err is None:
    print(ev.stats)
else:
    print(f"\nConstraint Violated: {err.name}\n")
    ev.replay_thunk(err.thunk)

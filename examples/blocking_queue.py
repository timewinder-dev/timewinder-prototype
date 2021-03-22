import timewinder

# These are the variables we'd like to modify to test
# bigger models.
PRODUCERS = 1
CONSUMERS = 1
QUEUE_SIZE = 3


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
    def __init__(self, num_threads):
        self.status = [True] * num_threads


@timewinder.process
def producer(queue, running, id):
    while True:
        while queue.is_full():
            running.status[id] = False
            yield "producer_paused"
        running.status[id] = True
        queue.queue.append(4)  # 4 represents arbitrary data
        yield "produced"


@timewinder.process
def consumer(queue, running, id):
    while True:
        while queue.is_empty():
            running.status[id] = False
            yield "consumer_paused"
        running.status[id] = True
        queue.queue.pop()
        yield "produced"


THREADS = PRODUCERS + CONSUMERS
runnable = ThreadCanRun(THREADS)
bqueue = BoundedQueue(QUEUE_SIZE)


threads = []
for i in range(PRODUCERS + CONSUMERS):
    if i < PRODUCERS:
        threads.append(producer(bqueue, runnable, i))
    else:
        threads.append(consumer(bqueue, runnable, i))

no_deadlocks = timewinder.ForAll(ThreadCanRun, lambda c: any(c.status))

ev = timewinder.Evaluator(
    objects=[runnable, bqueue],
    specs=[no_deadlocks],
    threads=threads,
)

err = None
try:
    ev.evaluate()
except timewinder.ConstraintError as e:
    err = e

if err is None:
    print(ev.stats)
else:
    print("\n" + err.name + "\n")
    ev.replay_thunk(err.thunk)

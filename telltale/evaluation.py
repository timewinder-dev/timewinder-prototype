from typing import Dict
from typing import List
from typing import Iterator

from copy import copy
from dataclasses import dataclass

from telltale.statetree import StateController
from telltale.statetree import MemoryCAS
from telltale.statetree import Hash

from .thread import Algorithm
from .thread import Step
from .thread import PCStack
from .thread import InitialStack
from .constraints import ConstraintError


@dataclass
class EvaluatorStats:
    thunk_runs: int = 0
    cas_objects: int = 0
    steps: int = 0


@dataclass
class EvalThunk:
    trace: List[int]
    current_threads: List[PCStack]
    state_id: Hash

    def thread_id(self) -> int:
        return self.trace[len(self.trace) - 1]


def _prepare_threads(threads) -> List[Algorithm]:
    out = []
    for t in threads:
        if isinstance(t, Algorithm):
            out.append(t)
        elif isinstance(t, Step):
            out.append(Algorithm(t))
        else:
            raise TypeError("Threads need to be prepared")
    return out


class Evaluator:
    def __init__(self, *, models=None, threads=None, specs=None):
        self.state_controller = StateController(MemoryCAS())
        if models is not None:
            for m in models:
                self.state_controller.mount(m._name, m)
        self.threads = _prepare_threads(threads)
        self.specs = [] if specs is None else specs
        self.state_space: Dict[int, List] = {}
        self._stats: EvaluatorStats = EvaluatorStats()

    def evaluate(self, steps: int = 5):
        self._stats = EvaluatorStats()
        initial_hashes = self.state_controller.commit()
        thread_state = [InitialStack] * len(self.threads)
        next_queue = []
        for h in initial_hashes:
            for i in range(len(self.threads)):
                next_queue.append(EvalThunk([i], thread_state[:], h))

        for step in range(1, steps + 1):
            state_queue = next_queue
            next_queue = []
            if len(state_queue) == 0:
                print("No more states to evaluate")
                break
            print(f"Evaluating Step {step}...")
            for thunk in state_queue:
                new_runs = self.run_thunk(thunk)
                next_queue.extend(new_runs)

    def check_constraints(self, t: EvalThunk):
        for spec in self.specs:
            models = self.state_controller.get_model_list()
            error = spec(models)
            if error is not None:
                error.trace = t.trace
                error.state = "\n".join([m.__repr__() for m in models])
                raise error

    def run_thunk(self, t: EvalThunk):
        self._stats.thunk_runs += 1
        algo = self.threads[t.thread_id()]
        self.state_controller.restore(t.state_id)

        current_stack: PCStack = t.current_threads[t.thread_id()]
        next_states = algo.execute_step(current_stack)
        next_hashes = self.state_controller.commit()
        try:
            self.check_constraints(t)
        except ConstraintError as e:
            raise e

        return self._generate_next(next_hashes, next_states, t)

    def _generate_next(
        self, next_hashes: Iterator[Hash], next_states: List[PCStack], t: EvalThunk
    ):
        new_pcs = []
        for s in next_states:
            new_threads = t.current_threads[:]
            new_threads[t.thread_id()] = s
            new_pcs.append(new_threads)

        to_run = []
        for h in next_hashes:
            for pcs in new_pcs:
                for i in range(len(self.threads)):
                    if pcs[i] == []:
                        continue
                    new_trace = t.trace[:]
                    new_trace.append(i)
                    to_run.append(
                        EvalThunk(
                            trace=new_trace,
                            current_threads=pcs[:],
                            state_id=h,
                        )
                    )
        return to_run

    def _print_state_space(self):
        self.state_controller.cas.debug_print()

    @property
    def stats(self) -> EvaluatorStats:
        s = copy(self._stats)
        s.cas_objects = self.state_controller.cas.size()
        return s

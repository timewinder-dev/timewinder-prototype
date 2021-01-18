from typing import List
from typing import Set

from copy import copy
from dataclasses import dataclass

from telltale.statetree import StateController
from telltale.statetree import MemoryCAS
from telltale.statetree import Hash

from .process import Process
from .process import Step
from .process import FuncProcess

from .constraints import ConstraintError


@dataclass
class EvaluatorStats:
    thread_executions: int = 0
    states: int = 0
    cas_objects: int = 0
    steps: int = 0
    final_states: int = 0


@dataclass
class EvalThunk:
    trace: List[int]
    state_hash: Hash


def _prepare_threads(threads) -> List[Process]:
    out = []
    for t in threads:
        if isinstance(t, Process):
            out.append(t)
        elif isinstance(t, Step):
            out.append(FuncProcess(t))
        else:
            raise TypeError("Threads need to be prepared")
    return out


class Evaluator:
    def __init__(self, *, models=None, threads: List = None, specs=None):
        self.state_controller = StateController(MemoryCAS())
        if models is not None:
            for m in models:
                self.state_controller.mount(m._name, m)
        if threads is None or len(threads) == 0:
            # We're doing static state space analysis
            raise NotImplementedError("Static analysis TBD")
        else:
            self.threads = _prepare_threads(threads)
            for i, t in enumerate(self.threads):
                self.state_controller.mount(f"_thread_{i}", t)
        self.specs = [] if specs is None else specs
        self._evaled_states: Set[bytes] = set()
        self._stats: EvaluatorStats = EvaluatorStats()

    def evaluate(self, steps: int = 5):
        self._stats = EvaluatorStats()
        initial_hashes = self.state_controller.commit()
        next_queue = []
        for h in initial_hashes:
            next_queue.append(EvalThunk(trace=[], state_hash=h))

        for step in range(1, steps + 1):
            state_queue = next_queue
            next_queue = []
            if len(state_queue) == 0:
                print("No more states to evaluate")
                break
            print(f"Evaluating Step {step}...")
            self._stats.steps += 1
            for thunk in state_queue:
                new_runs = self._eval_state(thunk)
                next_queue.extend(new_runs)

    def _check_constraints(self, trace: List[int]):
        for spec in self.specs:
            models = self.state_controller.get_model_list()
            error = spec(models)
            if error is not None:
                error.trace = trace
                error.state = "\n".join([m.__repr__() for m in models])
                raise error

    def _eval_state(self, t: EvalThunk) -> List[EvalThunk]:
        if t.state_hash.bytes in self._evaled_states:
            return []
        self._stats.states += 1
        self._evaled_states.add(t.state_hash.bytes)
        self.state_controller.restore(t.state_hash)
        try:
            self._check_constraints(t.trace)
        except ConstraintError as e:
            raise e
        runnable_threads = [i for i, t in enumerate(self.threads) if t.can_execute()]
        if len(runnable_threads) == 0:
            self._stats.final_states += 1
            # TODO: Check for deadlocking when awaiting
            return []
        return self._execute_threads(runnable_threads, t)

    def _execute_threads(self, thread_ids: List[int], t: EvalThunk):
        pre_restored = True
        out = []
        for thread_id in thread_ids:
            if pre_restored:
                pre_restored = False
            else:
                self.state_controller.restore(t.state_hash)
            this_trace = t.trace[:]
            this_trace.append(thread_id)
            thread = self.threads[thread_id]
            self._stats.thread_executions += 1
            thread.execute()
            next_hashes = self.state_controller.commit()
            for h in next_hashes:
                out.append(EvalThunk(trace=this_trace, state_hash=h))
        return out

    def _print_state_space(self):
        self.state_controller.cas.debug_print()

    @property
    def stats(self) -> EvaluatorStats:
        s = copy(self._stats)
        s.cas_objects = self.state_controller.cas.size()
        return s

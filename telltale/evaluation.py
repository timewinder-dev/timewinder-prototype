from typing import Dict
from typing import DefaultDict
from typing import List
from typing import Tuple

from dataclasses import dataclass

from collections import defaultdict
from .thread import Algorithm
from .thread import Step
from .constraints import ConstraintError
from .expanders import expand_states


@dataclass
class EvaluatorStats:
    thunk_runs: int = 0
    states: int = 0
    steps: int = 0


@dataclass
class EvalThunk:
    trace: List[int]
    current_threads: List[int]
    state_id: int

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
        self.models = [] if models is None else models
        self.threads = _prepare_threads(threads)
        self.specs = [] if specs is None else specs
        self.state_space: Dict[int, List] = {}
        self.evaluated: DefaultDict[Tuple[int, int], bool] = defaultdict(bool)
        self.stats: EvaluatorStats = EvaluatorStats()

    def _restore_state(self, state_vector):
        for model, state in zip(self.models, state_vector):
            model.restore_state(state)

    def _save_state(self) -> List:
        return [x.save_state() for x in self.models]

    def _add_state(self, state_vector) -> int:
        state_id = state_hash([state_hash(x) for x in state_vector])
        if state_id in self.state_space:
            return state_id
        self.stats.states += 1
        self.state_space[state_id] = state_vector
        return state_id

    def evaluate(self, steps: int = 5):
        self.stats = EvaluatorStats()
        initial_states = expand_states(self.models)
        initial_ids = (self._add_state(state) for state in initial_states)
        thread_state = [0] * len(self.threads)
        next_queue = []
        for init_id in initial_ids:
            next_queue.extend(
                [
                    EvalThunk([i], thread_state[:], init_id)
                    for i in range(len(self.threads))
                ]
            )

        for step in range(1, steps + 1):
            state_queue = next_queue
            next_queue = []
            if len(state_queue) == 0:
                print("No more states to evaluate")
                break
            print(f"Evaluating Step {step}...")
            self.stats.steps += 1
            for thunk in state_queue:
                new_runs = self.run_thunk(thunk)
                next_queue.extend(new_runs)

    def check_constraints(self, t: EvalThunk):
        for spec in self.specs:
            error = spec(self.models)
            if error is not None:
                error.trace = t.trace
                error.state = "\n".join([m.__repr__() for m in self.models])
                raise error

    def run_thunk(self, t: EvalThunk):
        self.stats.thunk_runs += 1
        self.evaluated[(t.state_id, t.thread_id())] = True
        algo = self.threads[t.thread_id()]
        self._restore_state(self.state_space[t.state_id])

        current_step: int = t.current_threads[t.thread_id()]
        algo.execute_step(current_step)
        state = self._save_state()
        gen_id = self._add_state(state)
        try:
            self.check_constraints(t)
        except ConstraintError as e:
            raise e
        next_states = algo.get_next_states(current_step)

        return self._generate_next(gen_id, next_states, t)

    def _generate_next(self, gen_id: int, next_states: List[int], t: EvalThunk):
        to_run = []
        for s in next_states:
            new_threads = t.current_threads[:]
            new_threads[t.thread_id()] = s
            for i in range(len(self.threads)):
                if new_threads[i] == -1:
                    continue
                if self.evaluated[(gen_id, i)]:
                    continue
                new_trace = t.trace[:]
                new_trace.append(i)
                to_run.append(
                    EvalThunk(
                        trace=new_trace,
                        current_threads=new_threads,
                        state_id=gen_id,
                    )
                )
        return to_run

    def _print_state_space(self):
        for n, states in self.state_space.items():
            print("")
            print(f"{n}:")
            for m in states:
                print(f"\t{m}")


def state_hash(item_list):
    vals = sorted(item_list)
    hashes = []
    for pair in vals:
        hashes.append(hash(pair))
    return hash(tuple(hashes))

from typing import Dict
from typing import DefaultDict
from typing import List
from typing import Tuple

from dataclasses import dataclass

from collections import defaultdict
from .thread import Algorithm
from .thread import Step


@dataclass
class EvaluatorStats:
    thunk_runs: int = 0
    states: int = 0
    steps: int = 0


@dataclass
class EvalThunk:
    thread_id: int
    current_threads: List[int]
    state_id: int


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
        self.models = models
        self.threads = _prepare_threads(threads)
        self.specs = specs
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
        initial_state = self._save_state()
        initial_id = self._add_state(initial_state)
        thread_state = [0] * len(self.threads)
        next_queue = [
            EvalThunk(i, thread_state[:], initial_id) for i in range(len(self.threads))
        ]

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

    def run_thunk(self, t: EvalThunk):
        self.stats.thunk_runs += 1
        self.evaluated[(t.state_id, t.thread_id)] = True
        algo = self.threads[t.thread_id]
        self._restore_state(self.state_space[t.state_id])

        current_step: int = t.current_threads[t.thread_id]
        algo.execute_step(current_step)
        state = self._save_state()
        gen_id = self._add_state(state)
        next_states = algo.get_next_states(current_step)

        to_run = []
        for s in next_states:
            new_threads = t.current_threads[:]
            new_threads[t.thread_id] = s
            for i in range(len(self.threads)):
                if new_threads[i] == -1:
                    continue
                if self.evaluated[(gen_id, i)]:
                    continue
                to_run.append(
                    EvalThunk(
                        thread_id=i,
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
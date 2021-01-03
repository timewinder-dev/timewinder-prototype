from typing import Dict
from typing import DefaultDict
from typing import List
from typing import Tuple

from dataclasses import dataclass

from collections import defaultdict
from .thread import _set_execution


@dataclass
class EvaluatorStats:
    thread_runs: int = 0
    states: int = 0
    steps: int = 0


class Evaluator:
    def __init__(self, *, models=None, threads=None, specs=None):
        self.models = models
        self.threads = threads
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
        next_queue = [(initial_id, i) for i in range(len(self.threads))]
        _set_execution(True)
        for step in range(1, steps + 1):
            state_queue = next_queue
            next_queue = []
            if len(state_queue) == 0:
                print("No more states to evaluate")
                break
            print(f"Evaluating Step {step}...")
            self.stats.steps += 1
            for state_id, thread_id in state_queue:
                new_runs = self.run_thread(state_id, thread_id)
                next_queue.extend(new_runs)
        _set_execution(False)

    def run_thread(self, state_id: int, thread_id: int):
        to_run = []
        self.stats.thread_runs += 1
        self.evaluated[(state_id, thread_id)] = True
        thread = self.threads[thread_id]
        self._restore_state(self.state_space[state_id])
        for _ in thread._eval():
            state = self._save_state()
            gen_id = self._add_state(state)
            for i in range(len(self.threads)):
                if i == thread_id:
                    continue
                if not self.evaluated[(gen_id, i)]:
                    to_run.append((gen_id, i))
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

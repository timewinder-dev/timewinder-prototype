from typing import Dict
from typing import DefaultDict
from typing import List

from collections import defaultdict
from .thread import _set_execution


class Evaluator:
    def __init__(self, *, models=None, threads=None, specs=None):
        self.models = models
        self.threads = threads
        self.specs = specs
        self.state_space: Dict[int, List] = {}
        self.evaluated: DefaultDict[int, bool] = defaultdict(bool)

    def _restore_state(self, state_vector):
        for model, state in zip(self.models, state_vector):
            model.restore_state(state)

    def _save_state(self) -> List:
        return [x.save_state() for x in self.models]

    def _add_state(self, state_vector) -> int:
        state_id = state_hash([state_hash(x) for x in state_vector])
        self.state_space[state_id] = state_vector
        return state_id

    def evaluate(self, steps=5):
        initial_state = self._save_state()
        initial_id = self._add_state(initial_state)
        next_queue = [initial_id]
        for step in range(1, steps + 1):
            state_queue = next_queue
            next_queue = []
            if len(state_queue) == 0:
                print(f"No more unique states to evaluate")
                break
            print(f"Evaluating Step {step}...")
            for state_id in state_queue:
                self.evaluated[state_id] = True
                for thread in self.threads:
                    self._restore_state(self.state_space[state_id])
                    _set_execution(True)
                    for ret in thread._eval():
                        state = self._save_state()
                        gen_id = self._add_state(state)
                        if not self.evaluated[gen_id]:
                            next_queue.append(gen_id)
                    _set_execution(False)
        self._print_state_space()

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

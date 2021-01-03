from typing import Dict
from typing import List


class Evaluator:
    def __init__(self, *, models=None, threads=None, specs=None):
        self.models = models
        self.threads = threads
        self.specs = specs
        self.state_space: Dict[int, List] = {}

    def _restore_state(self, state_vector):
        for model, state in zip(self.models, state_vector):
            model.restore_state(state)

    def _save_state(self) -> List:
        return [x.save_state() for x in self.models]

    def _add_state(self, state_vector) -> int:
        state_id = state_hash([state_hash(x.items()) for x in state_vector])
        self.state_space[state_id] = state_vector
        return state_id

    def evaluate(self, steps=5):
        initial_state = self._save_state()
        initial_id = self._add_state(initial_state)
        next_queue = [initial_id]
        for step in range(steps):
            state_queue = next_queue
            next_queue = []
            for state_id in state_queue:
                for thread in self.threads:
                    self._restore_state(self.state_space[state_id])



def state_hash(item_list):
    vals = sorted(item_list)
    hashes = []
    for pair in vals:
        hashes.append(hash(pair))
    return hash(hashes)

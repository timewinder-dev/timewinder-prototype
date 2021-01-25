from typing import List
from typing import Set

from copy import copy
from dataclasses import dataclass
from inspect import isfunction

from telltale.statetree import StateController
from telltale.statetree import MemoryCAS
from telltale.statetree import Hash

from .ltl import TTrace
from .ltl import LTLOp
from .ltl import Always

from .process import Process
from .process import Step
from .process import FuncProcess

from .predicate import ConstraintError
from .predicate import Predicate
from .predicate import predicate


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
    hashes: List[Hash]
    predicate_traces: List[TTrace]

    def state_hash(self) -> Hash:
        return self.hashes[-1]

    def initial_hash(self) -> Hash:
        return self.hashes[0]

    def clone(self) -> "EvalThunk":
        return EvalThunk(
            trace=self.trace[:],
            hashes=self.hashes[:],
            predicate_traces=[x.clone() for x in self.predicate_traces],
        )


def _prepare_threads(threads) -> List[Process]:
    out = []
    for t in threads:
        if isinstance(t, Process):
            out.append(t)
        elif isinstance(t, Step):
            out.append(FuncProcess(t))
        else:
            raise TypeError(f"Thread {t} need to be prepared, got {type(t)}")
    return out


def _prepare_specs(specs) -> List[LTLOp]:
    if specs is None:
        return []
    out = []
    for s in specs:
        if isinstance(s, LTLOp):
            out.append(s)
        elif isinstance(s, Predicate):
            out.append(Always(s))
        elif isfunction(s):
            out.append(Always(predicate(s)))
        else:
            raise TypeError(f"Spec {s} isn't a Predicate or an Op, got {type(s)}")
    return out


class Evaluator:
    def __init__(self, *, models=None, threads: List = None, specs: List = None):
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
        self.specs = _prepare_specs(specs)
        self._evaled_states: Set[bytes] = set()
        self._stats: EvaluatorStats = EvaluatorStats()

    def _initialize_evaluation(self):
        self._stats = EvaluatorStats()
        preds: List[List[Predicate]] = [s.get_predicates() for s in self.specs]
        # Flatten the list
        self.preds = [item for sub in preds for item in sub]
        for i, p in enumerate(self.preds):
            p.set_index(i)

    def evaluate(self, steps: int = 5):
        self._initialize_evaluation()
        initial_hashes = self.state_controller.commit()
        next_queue = []
        for h in initial_hashes:
            pred_traces = [TTrace([]) for i in self.preds]
            next_queue.append(
                EvalThunk(trace=[], hashes=[h], predicate_traces=pred_traces)
            )

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

    def _eval_preds(self, t: EvalThunk):
        for i, p in enumerate(self.preds):
            b = p.check(self.state_controller)
            t.predicate_traces[i].append(b)

    def _check_constraints(self, t: EvalThunk):
        for spec in self.specs:
            # TODO: check for stutter
            trace = spec.eval_traces(t.predicate_traces)
            ok = trace[0]
            if not ok:
                err = ConstraintError(str(spec))
                err.thunk = t
                err.state = self.state_controller.tree
                raise err

    def _eval_state(self, t: EvalThunk) -> List[EvalThunk]:
        if t.state_hash().bytes in self._evaled_states:
            return []
        self._stats.states += 1
        self._evaled_states.add(t.state_hash().bytes)
        self.state_controller.restore(t.state_hash())
        self._eval_preds(t)
        try:
            self._check_constraints(t)
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
                self.state_controller.restore(t.state_hash())
            new_thunk = t.clone()
            new_thunk.trace.append(thread_id)
            thread = self.threads[thread_id]
            self._stats.thread_executions += 1
            thread.execute(self.state_controller)
            next_hashes = self.state_controller.commit()
            for h in next_hashes:
                t_with_hash = new_thunk.clone()
                t_with_hash.hashes.append(h)
                out.append(t_with_hash)
        return out

    def replay_thunk(self, t: EvalThunk):
        self.state_controller.restore(t.initial_hash())
        print(self.state_controller.tree)
        step = 0
        for i in t.trace:
            step += 1
            print("Step %d" % step)
            self._execute_threads([i], t)
            print("Post-step-%d-state: " % step)
            print(self.state_controller.tree)

    def _print_state_space(self):
        self.state_controller.cas.debug_print()

    @property
    def stats(self) -> EvaluatorStats:
        s = copy(self._stats)
        s.cas_objects = self.state_controller.cas.size()
        return s

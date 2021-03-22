from typing import List
from typing import Set
from typing import Optional

from copy import copy
from dataclasses import dataclass
from dataclasses import field
from inspect import isfunction

from timewinder.statetree import StateController
from timewinder.statetree import MemoryCAS
from timewinder.statetree import Hash
from timewinder.pause import Fairness

from .ltl import TTrace
from .ltl import LTLOp
from .ltl import Always

from .process import Process
from .process import Step
from .process import FuncProcess

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
    # hashes is one longer than trace.
    # it's roughly a graph with edges
    # hashes[n] --trace[n]--> hashes[n + 1]
    hashes: List[Hash]
    predicate_traces: List[TTrace]
    must_run: List[int] = field(default_factory=list)

    def state_hash(self) -> Hash:
        return self.hashes[-1]

    def initial_hash(self) -> Hash:
        return self.hashes[0]

    def clone(self) -> "EvalThunk":
        return EvalThunk(
            trace=self.trace[:],
            hashes=self.hashes[:],
            predicate_traces=[x.clone() for x in self.predicate_traces],
            must_run=self.must_run[:],
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
    def __init__(self, *, objects=None, threads: List = None, specs: List = None):
        self.state_controller = StateController(MemoryCAS())
        if objects is not None:
            for m in objects:
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

    def evaluate(self, steps: Optional[int] = 5):
        self._initialize_evaluation()
        initial_hashes = self.state_controller.commit()
        next_queue = []
        for h in initial_hashes:
            pred_traces = [TTrace([]) for i in self.preds]
            next_queue.append(
                EvalThunk(trace=[], hashes=[h], predicate_traces=pred_traces)
            )

        if steps is None:
            steps = 2 ** 30
        for step in range(1, steps + 1):
            state_queue = next_queue
            next_queue = []
            if len(state_queue) == 0:
                print("No more states to evaluate")
                break
            print(f"Evaluating Step {step} ({len(state_queue)} states)...")
            self._stats.steps += 1
            for thunk in state_queue:
                new_runs = self._eval_state(thunk)
                next_queue.extend(new_runs)

    def _eval_preds(self, t: EvalThunk):
        for i, p in enumerate(self.preds):
            b = p.check(self.state_controller)
            t.predicate_traces[i].append(b)

    def _should_stutter(self) -> bool:
        # TODO: Fairness, etc.
        return True

    def _check_liveness(self, spec, t: EvalThunk):
        if self._should_stutter():
            trace = spec.eval_traces(t.predicate_traces)
            ok = trace[0]
            if not ok:
                err = StutterConstraintError(str(spec))
                err.thunk = t
                err.state = self.state_controller.tree
                raise err

    def _check_safety(self, spec, t: EvalThunk):
        trace = spec.eval_traces(t.predicate_traces)
        ok = trace[0]
        if not ok:
            err = ConstraintError(str(spec))
            err.thunk = t
            err.state = self.state_controller.tree
            raise err

    def _check_constraints(self, t: EvalThunk):
        for spec in self.specs:
            if spec.is_liveness():
                self._check_liveness(spec, t)
            else:
                self._check_safety(spec, t)

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
        if len(t.must_run) == 0:
            runnable_threads = [
                i for i, t in enumerate(self.threads) if t.can_execute()
            ]
        else:
            runnable_threads = t.must_run

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
            new_thunk.must_run = []
            new_thunk.trace.append(thread_id)
            thread = self.threads[thread_id]
            self._stats.thread_executions += 1
            cont = thread.execute(self.state_controller)
            next_hashes = self.state_controller.commit()
            for h in next_hashes:
                t_with_hash = new_thunk.clone()
                t_with_hash.hashes.append(h)
                if cont.fairness == Fairness.IMMEDIATE:
                    t_with_hash.must_run = [thread_id]
                out.append(t_with_hash)
        return out

    def replay_thunk(self, t: EvalThunk):
        print("Initial State:")
        self.state_controller.restore(t.initial_hash())
        print(self.state_controller.state_to_str())
        prev_hash = t.initial_hash()
        step = 0
        for tid, hash in zip(t.trace, t.hashes[1:]):
            step += 1
            print(f"Step {step}, thread {tid} executes")
            print(f"{prev_hash.hex()[:7]} -- {tid} --> {hash.hex()[:7]}")
            print("*" * 26)
            print("State: ")
            self.state_controller.restore(hash)
            print(self.state_controller.state_to_str())
            prev_hash = hash

    def _print_state_space(self):
        self.state_controller.cas.debug_print()

    @property
    def stats(self) -> EvaluatorStats:
        s = copy(self._stats)
        s.cas_objects = self.state_controller.cas.size()
        return s


class ConstraintError(BaseException):
    def __init__(self, name, thunk=None):
        self.name = name
        self.thunk = thunk
        self.state = None


class StutterConstraintError(ConstraintError):
    pass

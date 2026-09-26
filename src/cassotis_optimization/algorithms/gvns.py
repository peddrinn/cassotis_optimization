"""
GVNS for the mono-objective versions of the problem (Entrega 1).

Structure (Aula 02, slides 36-38):

    X <- local search(construct_initial_solution())
    while budget not exhausted:
        k <- 1
        while k <= k_max:
            X'  <- SHAKE(X, P_k)             # k * shake_moves_per_k random moves
            X'' <- VND(X', N1, N2, N3)       # first improvement in each N_l
            if X'' better than X: X <- X''; k <- 1
            else: k <- k + 1

"Better" follows the feasibility rule (D007). The stopping criterion is a fixed
number of solution evaluations (D010). All decisions are justified in
docs/decision_log.md and docs/gvns_decisoes.md.
"""

from __future__ import annotations

import random
import time
from dataclasses import asdict, dataclass, field

from cassotis_optimization.algorithms.constructive import construct_initial_solution
from cassotis_optimization.algorithms.vizinhancas import (
    ENUMERATORS,
    SAMPLERS,
    Move,
    apply_move,
)
from cassotis_optimization.domain import ProblemInstance
from cassotis_optimization.evaluator import Evaluation, evaluate
from cassotis_optimization.feasibility import feasibility_rule_key, normalized_violation
from cassotis_optimization.objectives import ObjectiveName, objective_value
from cassotis_optimization.solution import Solution


@dataclass(frozen=True)
class GVNSConfig:
    objective: ObjectiveName
    seed: int = 0
    max_evaluations: int = 200_000
    k_max: int = 3
    shake_moves_per_k: int = 3
    neighborhood_order: tuple[str, ...] = ("N1", "N2", "N3")
    # Neighborhoods explored exhaustively (in random order) by the local search.
    # The others are explored through ``sample_size`` random moves per pass (D014).
    exhaustive_neighborhoods: tuple[str, ...] = ("N1",)
    sample_size: int = 500


@dataclass(frozen=True)
class Candidate:
    solution: Solution
    evaluation: Evaluation
    violation: float
    objective: float

    @property
    def feasible(self) -> bool:
        return self.evaluation.feasible

    @property
    def key(self) -> tuple[int, float, float]:
        return feasibility_rule_key(self.feasible, self.violation, self.objective)


# Relative tolerance used to ignore floating-point noise when comparing keys.
_TOLERANCE = 1e-12


def is_better(a: Candidate, b: Candidate) -> bool:
    """Strict improvement of ``a`` over ``b`` under the feasibility rule."""

    if a.key[0] != b.key[0]:
        return a.key[0] < b.key[0]

    for value_a, value_b in zip(a.key[1:], b.key[1:]):
        margin = _TOLERANCE * max(1.0, abs(value_a), abs(value_b))
        if value_a < value_b - margin:
            return True
        if value_a > value_b + margin:
            return False

    return False


class BudgetExhausted(Exception):
    pass


@dataclass
class HistoryPoint:
    evaluations: int
    feasible: bool
    objective: float
    violation: float


class CountingEvaluator:
    """Evaluates solutions, counts evaluations and keeps the best-so-far curve."""

    def __init__(
        self,
        instance: ProblemInstance,
        objective: ObjectiveName,
        max_evaluations: int,
    ) -> None:
        self.instance = instance
        self.objective = objective
        self.max_evaluations = max_evaluations
        self.evaluations = 0
        self.best: Candidate | None = None
        self.history: list[HistoryPoint] = []
        self.first_feasible_at: int | None = None

    def __call__(self, solution: Solution) -> Candidate:
        if self.evaluations >= self.max_evaluations:
            raise BudgetExhausted

        evaluation = evaluate(solution, self.instance)
        self.evaluations += 1

        candidate = Candidate(
            solution=solution,
            evaluation=evaluation,
            violation=normalized_violation(evaluation, self.instance).total,
            objective=objective_value(evaluation, self.objective),
        )

        if self.best is None or is_better(candidate, self.best):
            self.best = candidate
            if candidate.feasible and self.first_feasible_at is None:
                self.first_feasible_at = self.evaluations
            self._record(candidate)

        return candidate

    def _record(self, candidate: Candidate) -> None:
        self.history.append(
            HistoryPoint(
                evaluations=self.evaluations,
                feasible=candidate.feasible,
                objective=candidate.objective,
                violation=candidate.violation,
            )
        )


@dataclass
class GVNSResult:
    config: GVNSConfig
    best: Candidate
    initial: Candidate
    history: list[HistoryPoint]
    evaluations: int
    iterations: int
    improvements: int
    first_feasible_at: int | None
    runtime_seconds: float
    stats: dict[str, int] = field(default_factory=dict)

    def history_as_dicts(self) -> list[dict]:
        return [asdict(point) for point in self.history]


class GVNS:
    def __init__(self, instance: ProblemInstance, config: GVNSConfig) -> None:
        self.instance = instance
        self.config = config
        self.rng = random.Random(config.seed)
        self.evaluator = CountingEvaluator(
            instance, config.objective, config.max_evaluations
        )
        self.stats = {f"improvements_{name}": 0 for name in config.neighborhood_order}

    # ------------------------------------------------------------------
    # Shake
    # ------------------------------------------------------------------

    def shake(self, solution: Solution, k: int) -> Solution:
        """P_k: apply k * shake_moves_per_k random moves drawn from N1/N2/N3."""

        for _ in range(k * self.config.shake_moves_per_k):
            name = self.rng.choice(self.config.neighborhood_order)
            move = SAMPLERS[name](solution, self.instance, self.rng)
            if move is not None:
                solution = apply_move(solution, move)
        return solution

    # ------------------------------------------------------------------
    # Local search and VND
    # ------------------------------------------------------------------

    def _candidate_moves(self, name: str, solution: Solution) -> list[Move]:
        if name in self.config.exhaustive_neighborhoods:
            moves = ENUMERATORS[name](solution, self.instance)
            self.rng.shuffle(moves)
            return moves

        sampler = SAMPLERS[name]
        moves = []
        for _ in range(self.config.sample_size):
            move = sampler(solution, self.instance, self.rng)
            if move is not None:
                moves.append(move)
        return moves

    def local_search(self, current: Candidate, name: str) -> Candidate:
        """First improvement in N_name, repeated until no improving move is found."""

        improved = True
        while improved:
            improved = False
            for move in self._candidate_moves(name, current.solution):
                neighbor = self.evaluator(apply_move(current.solution, move))
                if is_better(neighbor, current):
                    current = neighbor
                    improved = True
                    self.stats[f"improvements_{name}"] += 1
                    break
        return current

    def vnd(self, current: Candidate) -> Candidate:
        order = self.config.neighborhood_order
        level = 0
        while level < len(order):
            candidate = self.local_search(current, order[level])
            if is_better(candidate, current):
                current = candidate
                level = 0
            else:
                level += 1
        return current

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> GVNSResult:
        start = time.perf_counter()
        iterations = 0
        improvements = 0

        initial = self.evaluator(construct_initial_solution(self.instance))
        current = initial

        try:
            current = self.vnd(current)

            while True:
                k = 1
                while k <= self.config.k_max:
                    iterations += 1
                    shaken = self.evaluator(self.shake(current.solution, k))
                    candidate = self.vnd(shaken)

                    if is_better(candidate, current):
                        current = candidate
                        improvements += 1
                        k = 1
                    else:
                        k += 1
        except BudgetExhausted:
            pass

        best = self.evaluator.best
        assert best is not None

        return GVNSResult(
            config=self.config,
            best=best,
            initial=initial,
            history=list(self.evaluator.history),
            evaluations=self.evaluator.evaluations,
            iterations=iterations,
            improvements=improvements,
            first_feasible_at=self.evaluator.first_feasible_at,
            runtime_seconds=time.perf_counter() - start,
            stats=dict(self.stats),
        )


def run_gvns(instance: ProblemInstance, config: GVNSConfig) -> GVNSResult:
    return GVNS(instance, config).run()

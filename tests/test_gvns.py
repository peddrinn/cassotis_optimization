import random
from pathlib import Path

import pytest

from cassotis_optimization.algorithms.constructive import construct_initial_solution
from cassotis_optimization.algorithms.gvns import GVNSConfig, is_better, run_gvns
from cassotis_optimization.algorithms.vizinhancas import (
    ENUMERATORS,
    SAMPLERS,
    apply_move,
)
from cassotis_optimization.evaluator import evaluate
from cassotis_optimization.io import load_instance


DATA_DIR = Path("data/example_instance")


def _assert_structure_preserved(solution, instance) -> None:
    for pile_id, pile in instance.piles.items():
        assert len(solution.composition[pile_id]) == pile.n_trucks
        for mineral_id in solution.composition[pile_id]:
            assert instance.minerals[mineral_id].is_eligible(pile.group_id)


@pytest.mark.parametrize("name", ["N1", "N2"])
def test_enumerated_moves_preserve_mass_and_eligibility(name) -> None:
    instance = load_instance(DATA_DIR)
    solution = construct_initial_solution(instance)

    moves = ENUMERATORS[name](solution, instance)

    assert moves
    assert len(set(moves)) == len(moves)
    for move in moves:
        _assert_structure_preserved(apply_move(solution, move), instance)


@pytest.mark.parametrize("name", ["N1", "N2", "N3"])
def test_sampled_moves_belong_to_the_enumerated_neighborhood(name) -> None:
    instance = load_instance(DATA_DIR)
    solution = construct_initial_solution(instance)
    rng = random.Random(7)

    enumerated = set(ENUMERATORS[name](solution, instance))

    for _ in range(200):
        move = SAMPLERS[name](solution, instance, rng)
        assert move in enumerated


def test_feasibility_rule_ordering() -> None:
    instance = load_instance(DATA_DIR)
    result = run_gvns(instance, GVNSConfig(objective="f1", seed=0, max_evaluations=3000))

    assert result.best.feasible
    assert not result.initial.feasible
    assert is_better(result.best, result.initial)
    assert not is_better(result.initial, result.best)


@pytest.mark.parametrize("objective", ["f1", "f2", "f3"])
def test_gvns_respects_budget_and_returns_consistent_best(objective) -> None:
    instance = load_instance(DATA_DIR)
    config = GVNSConfig(objective=objective, seed=3, max_evaluations=4000)

    result = run_gvns(instance, config)

    assert result.evaluations == config.max_evaluations
    _assert_structure_preserved(result.best.solution, instance)

    evaluation = evaluate(result.best.solution, instance)
    assert evaluation.feasible == result.best.feasible
    assert evaluation.cost_rs == result.best.evaluation.cost_rs


def test_convergence_history_is_monotone() -> None:
    instance = load_instance(DATA_DIR)
    result = run_gvns(instance, GVNSConfig(objective="f2", seed=5, max_evaluations=4000))

    evaluations = [p.evaluations for p in result.history]
    assert evaluations == sorted(evaluations)

    feasible_values = [p.objective for p in result.history if p.feasible]
    assert feasible_values == sorted(feasible_values, reverse=True)

    # Once feasible, the best-so-far never becomes infeasible again.
    flags = [p.feasible for p in result.history]
    assert flags == sorted(flags)


def test_gvns_is_reproducible_with_same_seed() -> None:
    instance = load_instance(DATA_DIR)
    config = GVNSConfig(objective="f3", seed=11, max_evaluations=3000)

    first = run_gvns(instance, config)
    second = run_gvns(instance, config)

    assert first.best.solution == second.best.solution
    assert first.history == second.history

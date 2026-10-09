
import json
from pathlib import Path

import pytest

from cassotis_optimization.multiobjective.multiobjective import (
    EpsilonLimits,
    Weights,
)
from cassotis_optimization.multiobjective.planejamento import (
    epsilon_grid,
    weight_grid,
)

PROTOCOL = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "protocolo_entrega2.json"
)


def test_weight_grid() -> None:
    grid = weight_grid(4, include_equal_weights=True)

    assert len(grid) == 16
    assert len(set(grid)) == 16

    for weights in grid:
        assert sum((weights.f1, weights.f2, weights.f3)) == pytest.approx(1.0)

    assert Weights(1.0, 0.0, 0.0) in grid
    assert Weights(0.0, 1.0, 0.0) in grid
    assert Weights(0.0, 0.0, 1.0) in grid
    assert Weights(1 / 3, 1 / 3, 1 / 3) in grid


def test_weight_grid_without_center() -> None:
    assert len(weight_grid(4, include_equal_weights=False)) == 15


def test_epsilon_grid() -> None:
    levels = (0.25, 0.5, 0.75, 1.0)
    grid = epsilon_grid(levels, levels)

    assert len(grid) == 16
    assert len(set(grid)) == 16

    assert EpsilonLimits(0.25, 0.25) in grid
    assert EpsilonLimits(1.0, 1.0) in grid


def test_experiment_protocol() -> None:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))

    weighted = protocol["weighted_sum"]
    epsilon = protocol["epsilon_restricted"]

    weights = weight_grid(
        weighted["simplex_denominator"],
        weighted["include_equal_weights"],
    )
    limits = epsilon_grid(
        epsilon["levels_f2"],
        epsilon["levels_f3"],
    )

    assert len(weights) == weighted["expected_configurations"] == 16
    assert len(limits) == epsilon["expected_configurations"] == 16

    pilot_seeds = protocol["pilot"]["seeds"]
    final_seeds = protocol["final"]["seeds"]

    assert len(final_seeds) == 5
    assert len(set(final_seeds)) == 5
    assert set(pilot_seeds).isdisjoint(final_seeds)
    assert set(final_seeds).isdisjoint(range(2016, 2021))

    budget = protocol["final"]["max_evaluations"]
    assert len(weights) * len(final_seeds) * budget == 16_000_000
    assert len(limits) * len(final_seeds) * budget == 16_000_000


def test_invalid_grids() -> None:
    with pytest.raises(ValueError):
        weight_grid(0)

    with pytest.raises(ValueError):
        epsilon_grid([], [0.5])

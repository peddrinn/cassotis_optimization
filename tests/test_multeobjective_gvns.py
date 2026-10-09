
from pathlib import Path

import pytest

from cassotis_optimization.algorithms.gvns import (
    CountingEvaluator,
    GVNSConfig,
    run_gvns,
)
from cassotis_optimization.feasibility import normalized_violation
from cassotis_optimization.io import load_instance
from cassotis_optimization.multiobjective.epsilon_restrito import (
    epsilon_objective,
    epsilon_violations,
)
from cassotis_optimization.multiobjective.multiobjective import (
    EpsilonLimits,
    Weights,
)
from cassotis_optimization.multiobjective.normalizacao import load_bounds
from cassotis_optimization.multiobjective.soma_ponderada import weighted_sum

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_FILE = ROOT / "data" / "referencias_multiobjetivo.json"
INSTANCE_DIR = ROOT / "data" / "example_instance"


@pytest.fixture(scope="module")
def example():
    instance = load_instance(INSTANCE_DIR)
    bounds = load_bounds(REFERENCE_FILE)

    # Obtém uma solução originalmente factível para testar
    # as diferentes classificações sem depender da nova GVNS.
    result = run_gvns(
        instance,
        GVNSConfig(
            objective="f1",
            seed=0,
            max_evaluations=4000,
        ),
    )

    assert result.best.evaluation.feasible

    return instance, bounds, result.best.solution


def test_weighted_sum_score(example) -> None:
    instance, bounds, solution = example
    weights = Weights(0.5, 0.25, 0.25)

    config = GVNSConfig(
        objective="weighted_sum",
        bounds=bounds,
        weights=weights,
    )

    candidate = CountingEvaluator(instance, config)(solution)

    assert candidate.feasible
    assert candidate.objective == pytest.approx(
        weighted_sum(candidate.evaluation, bounds, weights)
    )


def test_epsilon_changes_search_feasibility(example) -> None:
    instance, bounds, solution = example

    # Limites permissivos.
    wide_config = GVNSConfig(
        objective="epsilon_restricted",
        bounds=bounds,
        epsilon_limits=EpsilonLimits(10.0, 10.0),
    )

    wide = CountingEvaluator(instance, wide_config)(solution)

    assert wide.evaluation.feasible
    assert wide.feasible

    # Limites mais restritivos que os valores da solução.
    tight_limits = EpsilonLimits(-10.0, -10.0)

    tight_config = GVNSConfig(
        objective="epsilon_restricted",
        bounds=bounds,
        epsilon_limits=tight_limits,
    )

    tight = CountingEvaluator(instance, tight_config)(solution)

    # A factibilidade ORIGINAL não foi alterada.
    assert tight.evaluation.feasible

    # A factibilidade do epsilon-restrito é diferente.
    assert not tight.feasible

    v2, v3 = epsilon_violations(
        tight.evaluation, bounds, tight_limits
    )

    original_violation = normalized_violation(
        tight.evaluation, instance
    ).total

    assert tight.violation == pytest.approx(
        original_violation + v2 + v3
    )

    assert tight.objective == pytest.approx(
        epsilon_objective(tight.evaluation, bounds)
    )


def test_invalid_multiobjective_config() -> None:
    with pytest.raises(ValueError):
        GVNSConfig(objective="weighted_sum")

    with pytest.raises(ValueError):
        GVNSConfig(objective="epsilon_restricted")

    with pytest.raises(ValueError):
        GVNSConfig(objective="unknown")


@pytest.mark.parametrize("mode", ["weighted_sum", "epsilon_restricted"])
def test_multiobjective_run_respects_budget(mode) -> None:
    instance = load_instance(INSTANCE_DIR)
    bounds = load_bounds(REFERENCE_FILE)

    if mode == "weighted_sum":
        config = GVNSConfig(
            objective="weighted_sum",
            bounds=bounds,
            weights=Weights(0.5, 0.25, 0.25),
            seed=3,
            max_evaluations=1000,
            sample_size=250,
        )
    else:
        config = GVNSConfig(
            objective="epsilon_restricted",
            bounds=bounds,
            epsilon_limits=EpsilonLimits(0.75, 0.75),
            seed=3,
            max_evaluations=1000,
            sample_size=250,
        )

    result = run_gvns(instance, config)

    assert result.evaluations == 1000
    assert result.best is not None
    assert result.best.violation >= 0.0

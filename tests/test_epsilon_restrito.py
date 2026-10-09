
import pytest

from cassotis_optimization.evaluator import Evaluation
from cassotis_optimization.multiobjective.epsilon_restrito import (
    epsilon_feasible,
    epsilon_objective,
    epsilon_violations,
)
from cassotis_optimization.multiobjective.multiobjective import (
    EpsilonLimits,
    ObjectiveBounds,
)


@pytest.fixture
def bounds() -> ObjectiveBounds:
    return ObjectiveBounds(
        ideal=(100.0, 2.0, 1.0),
        reference=(200.0, 6.0, 5.0),
    )


def make_evaluation(
    f1: float,
    f2: float,
    f3: float,
    feasible: bool = True,
) -> Evaluation:
    return Evaluation(
        cost_rs=f1,
        f2_sio2_sq_dev=f2,
        f3_al2o3_sq_dev=f3,
        feasible=feasible,
        violations={} if feasible else {"test": 1.0},
        quality_by_pile={},
        usage_by_mineral={},
    )


def test_epsilon_objective_is_normalized_cost(
    bounds: ObjectiveBounds,
) -> None:
    evaluation = make_evaluation(150.0, 4.0, 3.0)

    assert epsilon_objective(evaluation, bounds) == pytest.approx(0.5)


def test_epsilon_violations_zero_when_satisfied(
    bounds: ObjectiveBounds,
) -> None:
    evaluation = make_evaluation(150.0, 4.0, 3.0)
    limits = EpsilonLimits(f2=0.5, f3=0.5)

    assert epsilon_violations(evaluation, bounds, limits) == (0.0, 0.0)
    assert epsilon_feasible(evaluation, bounds, limits)


def test_epsilon_violations_when_exceeded(
    bounds: ObjectiveBounds,
) -> None:
    evaluation = make_evaluation(150.0, 5.0, 4.0)
    limits = EpsilonLimits(f2=0.5, f3=0.25)

    # Objetivos normalizados: (0.5, 0.75, 0.75)
    v2, v3 = epsilon_violations(evaluation, bounds, limits)

    assert v2 == pytest.approx(0.25)
    assert v3 == pytest.approx(0.50)
    assert not epsilon_feasible(evaluation, bounds, limits)


def test_original_infeasibility_is_preserved(
    bounds: ObjectiveBounds,
) -> None:
    evaluation = make_evaluation(
        150.0, 4.0, 3.0, feasible=False
    )
    limits = EpsilonLimits(f2=0.5, f3=0.5)

    # Epsilon é satisfeito, mas o problema original não.
    assert epsilon_violations(evaluation, bounds, limits) == (0.0, 0.0)
    assert not epsilon_feasible(evaluation, bounds, limits)


@pytest.mark.parametrize(
    "limits",
    [
        (float("nan"), 0.5),
        (0.5, float("inf")),
        (float("-inf"), 1.0),
    ],
)
def test_invalid_epsilon_limits(
    limits: tuple[float, float],
) -> None:
    with pytest.raises(ValueError):
        EpsilonLimits(*limits)

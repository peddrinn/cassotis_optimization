
import pytest

from cassotis_optimization.evaluator import Evaluation
from cassotis_optimization.multiobjective.multiobjective import (
    ObjectiveBounds,
    Weights,
)
from cassotis_optimization.multiobjective.soma_ponderada import (
    weighted_sum,
)


def make_evaluation(f1: float, f2: float, f3: float) -> Evaluation:
    return Evaluation(
        cost_rs=f1,
        f2_sio2_sq_dev=f2,
        f3_al2o3_sq_dev=f3,
        feasible=True,
        violations={},
        quality_by_pile={},
        usage_by_mineral={},
    )


@pytest.fixture
def bounds() -> ObjectiveBounds:
    return ObjectiveBounds(
        ideal=(100.0, 2.0, 1.0),
        reference=(200.0, 6.0, 5.0),
    )


def test_equal_weights(bounds: ObjectiveBounds) -> None:
    evaluation = make_evaluation(150.0, 4.0, 5.0)
    weights = Weights(1 / 3, 1 / 3, 1 / 3)

    # Objetivos normalizados: (0.5, 0.5, 1.0)
    expected = (0.5 + 0.5 + 1.0) / 3

    assert weighted_sum(evaluation, bounds, weights) == pytest.approx(expected)


def test_different_weights(bounds: ObjectiveBounds) -> None:
    evaluation = make_evaluation(150.0, 4.0, 5.0)
    weights = Weights(0.5, 0.25, 0.25)

    expected = 0.5 * 0.5 + 0.25 * 0.5 + 0.25 * 1.0

    assert weighted_sum(evaluation, bounds, weights) == pytest.approx(0.625)
    assert weighted_sum(evaluation, bounds, weights) == pytest.approx(expected)


def test_single_objective_weights(bounds: ObjectiveBounds) -> None:
    evaluation = make_evaluation(150.0, 4.0, 5.0)

    assert weighted_sum(
        evaluation, bounds, Weights(1.0, 0.0, 0.0)
    ) == pytest.approx(0.5)

    assert weighted_sum(
        evaluation, bounds, Weights(0.0, 0.0, 1.0)
    ) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "values",
    [
        (-0.1, 0.5, 0.6),
        (0.5, 0.5, 0.5),
        (0.0, 0.0, 0.0),
        (float("nan"), 0.5, 0.5),
        (float("inf"), 0.0, 0.0),
    ],
)
def test_invalid_weights(values: tuple[float, float, float]) -> None:
    with pytest.raises(ValueError):
        Weights(*values)

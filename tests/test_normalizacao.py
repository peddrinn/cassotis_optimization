
from pathlib import Path

import pytest

from cassotis_optimization.evaluator import Evaluation
from cassotis_optimization.multiobjective.multiobjective import ObjectiveBounds
from cassotis_optimization.multiobjective.normalizacao import (
    load_bounds,
    normalize,
    normalized_objectives,
)

REFERENCE_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "referencias_multiobjetivo.json"
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


def test_reference_file() -> None:
    bounds = load_bounds(REFERENCE_FILE)

    assert bounds.ideal == pytest.approx(
        (59700000.0, 2.3730254273702003, 1.4207622050785091)
    )
    assert bounds.reference == pytest.approx(
        (65820000.0, 6.497711698958577, 6.537507381189193)
    )


def test_normalize() -> None:
    assert normalize(10.0, 10.0, 20.0) == pytest.approx(0.0)
    assert normalize(20.0, 10.0, 20.0) == pytest.approx(1.0)
    assert normalize(15.0, 10.0, 20.0) == pytest.approx(0.5)


def test_normalization_without_clipping() -> None:
    assert normalize(5.0, 10.0, 20.0) == pytest.approx(-0.5)
    assert normalize(25.0, 10.0, 20.0) == pytest.approx(1.5)


def test_anchor_x1() -> None:
    bounds = load_bounds(REFERENCE_FILE)
    evaluation = make_evaluation(
        59700000.0,
        6.497711698958577,
        6.537507381189193,
    )

    assert normalized_objectives(evaluation, bounds) == pytest.approx(
        (0.0, 1.0, 1.0)
    )


def test_anchor_x2() -> None:
    bounds = load_bounds(REFERENCE_FILE)
    evaluation = make_evaluation(
        63440000.0,
        2.3730254273702003,
        3.635610446744914,
    )

    normalized = normalized_objectives(evaluation, bounds)
    assert normalized[1] == pytest.approx(0.0)


def test_anchor_x3() -> None:
    bounds = load_bounds(REFERENCE_FILE)
    evaluation = make_evaluation(
        65820000.0,
        6.339640659482665,
        1.4207622050785091,
    )

    normalized = normalized_objectives(evaluation, bounds)
    assert normalized[0] == pytest.approx(1.0)
    assert normalized[2] == pytest.approx(0.0)


def test_invalid_interval() -> None:
    with pytest.raises(ValueError):
        normalize(5.0, 10.0, 10.0)

    with pytest.raises(ValueError):
        ObjectiveBounds(
            ideal=(1.0, 2.0, 3.0),
            reference=(1.0, 4.0, 5.0),
        )


import json
from math import isclose
from pathlib import Path

from cassotis_optimization.evaluator import Evaluation
from cassotis_optimization.multiobjective.multiobjective import ObjectiveBounds


def load_bounds(path: str | Path) -> ObjectiveBounds:
    """Carrega e valida as referências da Entrega 1."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    bounds = ObjectiveBounds(
        ideal=tuple(data["ideal_point"]["z_star"]),
        reference=tuple(data["nadir_reference"]["z_ref"]),
    )

    anchors = [anchor["f"] for anchor in data["anchor_solutions"]]

    if len(anchors) != 3 or any(len(anchor) != 3 for anchor in anchors):
        raise ValueError("São necessárias três soluções-âncora completas.")

    for j in range(3):
        expected_ideal = min(anchor[j] for anchor in anchors)
        expected_reference = max(anchor[j] for anchor in anchors)

        if not isclose(bounds.ideal[j], expected_ideal, rel_tol=1e-12):
            raise ValueError("Ideal inconsistente com as soluções-âncora.")

        if not isclose(bounds.reference[j], expected_reference, rel_tol=1e-12):
            raise ValueError("Referência superior inconsistente com as âncoras.")

    return bounds


def normalize(value: float, ideal: float, reference: float) -> float:
    """Normalização min–max sem truncamento em [0, 1]."""
    if reference <= ideal:
        raise ValueError("O intervalo de normalização deve ser positivo.")

    return (value - ideal) / (reference - ideal)


def normalized_objectives(
    evaluation: Evaluation,
    bounds: ObjectiveBounds,
) -> tuple[float, float, float]:
    """Normaliza simultaneamente f1, f2 e f3."""
    values = (
        evaluation.cost_rs,
        evaluation.f2_sio2_sq_dev,
        evaluation.f3_al2o3_sq_dev,
    )

    return (
        normalize(values[0], bounds.ideal[0], bounds.reference[0]),
        normalize(values[1], bounds.ideal[1], bounds.reference[1]),
        normalize(values[2], bounds.ideal[2], bounds.reference[2]),
    )

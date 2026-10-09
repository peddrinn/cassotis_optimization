
from __future__ import annotations

from cassotis_optimization.evaluator import Evaluation

from .multiobjective import ObjectiveBounds, Weights
from .normalizacao import normalized_objectives


def weighted_sum(
    evaluation: Evaluation,
    bounds: ObjectiveBounds,
    weights: Weights,
) -> float:
    """Calcula a soma ponderada dos três objetivos normalizados."""

    f1, f2, f3 = normalized_objectives(evaluation, bounds)

    return (
        weights.f1 * f1
        + weights.f2 * f2
        + weights.f3 * f3
    )

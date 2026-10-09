
from __future__ import annotations

from cassotis_optimization.evaluator import Evaluation

from .multiobjective import EpsilonLimits, ObjectiveBounds
from .normalizacao import normalized_objectives


def epsilon_objective(
    evaluation: Evaluation,
    bounds: ObjectiveBounds,
) -> float:
    """Objetivo principal: custo normalizado."""
    f1, _, _ = normalized_objectives(evaluation, bounds)
    return f1


def epsilon_violations(
    evaluation: Evaluation,
    bounds: ObjectiveBounds,
    limits: EpsilonLimits,
) -> tuple[float, float]:
    """Retorna as violações das duas restrições epsilon."""
    _, f2, f3 = normalized_objectives(evaluation, bounds)

    v2 = max(0.0, f2 - limits.f2)
    v3 = max(0.0, f3 - limits.f3)

    return v2, v3


def epsilon_feasible(
    evaluation: Evaluation,
    bounds: ObjectiveBounds,
    limits: EpsilonLimits,
) -> bool:
    """Factibilidade original mais as restrições epsilon."""
    v2, v3 = epsilon_violations(evaluation, bounds, limits)

    return evaluation.feasible and v2 == 0.0 and v3 == 0.0

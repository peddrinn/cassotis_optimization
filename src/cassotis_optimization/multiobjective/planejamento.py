
from __future__ import annotations

from collections.abc import Sequence
from itertools import product

from .multiobjective import EpsilonLimits, Weights


def weight_grid(
    denominator: int = 4,
    include_equal_weights: bool = True,
) -> tuple[Weights, ...]:
    """Gera uma grade simplex-lattice para três objetivos."""
    if denominator < 1:
        raise ValueError("O denominador deve ser positivo.")

    points = [
        Weights(k1 / denominator, k2 / denominator, k3 / denominator)
        for k1, k2, k3 in product(range(denominator + 1), repeat=3)
        if k1 + k2 + k3 == denominator
    ]

    # O centro já pertence à malha se o denominador for múltiplo de 3.
    if include_equal_weights and denominator % 3 != 0:
        points.append(Weights(1 / 3, 1 / 3, 1 / 3))

    return tuple(points)


def epsilon_grid(
    levels_f2: Sequence[float],
    levels_f3: Sequence[float],
) -> tuple[EpsilonLimits, ...]:
    """Gera o produto cartesiano dos limites epsilon."""
    if not levels_f2 or not levels_f3:
        raise ValueError("As listas de epsilon não podem estar vazias.")

    return tuple(
        EpsilonLimits(f2=e2, f3=e3)
        for e2, e3 in product(levels_f2, levels_f3)
    )

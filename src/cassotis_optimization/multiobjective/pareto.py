"""Filtro de Pareto em tres objetivos originais, todos de minimizacao (D021)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


OBJECTIVE_KEYS = ("f1", "f2", "f3")


def dominates(a: Mapping, b: Mapping) -> bool:
    """a domina b iff nao piora nenhum objetivo e melhora pelo menos um."""
    return (
        all(a[k] <= b[k] for k in OBJECTIVE_KEYS)
        and any(a[k] < b[k] for k in OBJECTIVE_KEYS)
    )


def nondominated_indices(rows: Sequence[Mapping]) -> list[int]:
    """Indices de pontos nao dominados em R3, mantendo empates/duplicatas.

    Os dados precisam ter sido previamente filtrados para factibilidade escalar.
    Nao usamos projecoes 2D ou objetivo escalar na definicao de dominancia.
    """
    return [
        i
        for i, candidate in enumerate(rows)
        if not any(dominates(other, candidate) for j, other in enumerate(rows) if i != j)
    ]

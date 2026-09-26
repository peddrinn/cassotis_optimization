from __future__ import annotations

import random

from cassotis_optimization.domain import ProblemInstance
from cassotis_optimization.solution import Solution


def n1_replace(
    solution: Solution,
    instance: ProblemInstance,
    rng: random.Random,
) -> Solution:
    """Replace one truck slot by another eligible mineral."""

    pile_id = rng.choice(list(instance.piles.keys()))
    pile = instance.piles[pile_id]

    current_composition = list(solution.composition[pile_id])

    position = rng.randrange(len(current_composition))
    current_mineral = current_composition[position]

    candidates = [
        mineral_id
        for mineral_id, mineral in instance.minerals.items()
        if (
            mineral_id != current_mineral
            and mineral.is_eligible(pile.group_id)
        )
    ]

    if not candidates:
        return solution

    new_mineral = rng.choice(candidates)

    current_composition[position] = new_mineral

    new_composition = dict(solution.composition)
    new_composition[pile_id] = tuple(current_composition)

    return Solution(composition=new_composition)
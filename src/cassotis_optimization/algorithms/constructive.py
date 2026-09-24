from __future__ import annotations

from cassotis_optimization.domain import ProblemInstance
from cassotis_optimization.solution import Solution


class ConstructionError(RuntimeError):
    """Raised when the constructive heuristic cannot complete a solution."""


def construct_initial_solution(
    instance: ProblemInstance,
) -> Solution:
    """
    Build a baseline initial solution.

    The construction:
    1. satisfies global minimum usage requirements;
    2. respects mineral eligibility;
    3. respects global maximum availability;
    4. fills remaining slots using cheapest eligible minerals.

    Quality constraints are not guaranteed at this stage.
    """

    composition: dict[str, list[str]] = {
        pile_id: []
        for pile_id in instance.piles
    }

    usage: dict[str, int] = {
        mineral_id: 0
        for mineral_id in instance.minerals
    }

    # ---------------------------------------------------------
    # Phase 1: satisfy minimum global availability
    # ---------------------------------------------------------

    for mineral_id in sorted(instance.minerals):
        mineral = instance.minerals[mineral_id]

        for _ in range(mineral.min_trucks):
            eligible_piles = []

            for pile_id, pile in instance.piles.items():
                has_space = (
                    len(composition[pile_id])
                    < pile.n_trucks
                )

                if (
                    has_space
                    and mineral.is_eligible(pile.group_id)
                ):
                    eligible_piles.append(pile_id)

            if not eligible_piles:
                raise ConstructionError(
                    f"Could not allocate minimum usage "
                    f"for mineral {mineral_id}."
                )

            # Prefer the pile with the largest proportion
            # of remaining free slots.
            chosen_pile = max(
                eligible_piles,
                key=lambda pile_id: (
                    (
                        instance.piles[pile_id].n_trucks
                        - len(composition[pile_id])
                    )
                    / instance.piles[pile_id].n_trucks
                ),
            )

            composition[chosen_pile].append(mineral_id)
            usage[mineral_id] += 1

    # ---------------------------------------------------------
    # Phase 2: fill remaining positions
    # ---------------------------------------------------------

    ordered_piles = sorted(instance.piles)

    while any(
        len(composition[pile_id])
        < instance.piles[pile_id].n_trucks
        for pile_id in ordered_piles
    ):
        progress = False

        for pile_id in ordered_piles:
            pile = instance.piles[pile_id]

            if len(composition[pile_id]) >= pile.n_trucks:
                continue

            candidates = [
                mineral
                for mineral in instance.minerals.values()
                if (
                    mineral.is_eligible(pile.group_id)
                    and usage[mineral.mineral_id]
                    < mineral.max_trucks
                )
            ]

            if not candidates:
                raise ConstructionError(
                    f"No eligible mineral with remaining "
                    f"availability for pile {pile_id}."
                )

            chosen = min(
                candidates,
                key=lambda mineral: (
                    mineral.price_rs_per_t,
                    mineral.mineral_id,
                ),
            )

            composition[pile_id].append(chosen.mineral_id)
            usage[chosen.mineral_id] += 1
            progress = True

        if not progress:
            raise ConstructionError(
                "Construction stopped before all piles were filled."
            )

    return Solution(
        {
            pile_id: tuple(minerals)
            for pile_id, minerals in composition.items()
        }
    )
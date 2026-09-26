from __future__ import annotations

import random
from collections.abc import Callable

from cassotis_optimization.domain import ProblemInstance
from cassotis_optimization.solution import Solution


# A move is a tuple of slot substitutions (pile_id, mineral_out, mineral_in).
#
#   N1: ((p, m_old, m_new),)
#   N2: ((p_a, m_a, m_b), (p_b, m_b, m_a))
#   N3: ((p_a, m_x, m_z), (p_b, m_y, m_x))
#
# Slots holding the same mineral inside a pile are interchangeable: choosing
# any of them yields the same pile composition. Moves are therefore defined
# over the distinct minerals of each pile, which removes duplicated neighbors
# without changing the set of reachable solutions (D014).
Substitution = tuple[str, str, str]
Move = tuple[Substitution, ...]


def apply_move(solution: Solution, move: Move) -> Solution:
    """Return a new solution with the move applied. The input is not modified."""

    new_composition = dict(solution.composition)

    for pile_id, mineral_out, mineral_in in move:
        slots = list(new_composition[pile_id])
        slots[slots.index(mineral_out)] = mineral_in
        new_composition[pile_id] = tuple(slots)

    return Solution(composition=new_composition)


def _distinct_minerals(solution: Solution, pile_id: str) -> list[str]:
    return sorted(set(solution.composition[pile_id]))


def _eligible_minerals(instance: ProblemInstance, group_id: str) -> list[str]:
    return [
        mineral_id
        for mineral_id, mineral in instance.minerals.items()
        if mineral.is_eligible(group_id)
    ]


# ---------------------------------------------------------------------------
# Full enumeration (used by the local search)
# ---------------------------------------------------------------------------


def n1_moves(solution: Solution, instance: ProblemInstance) -> list[Move]:
    """All N1 moves: replace one mineral of a pile by another eligible mineral."""

    moves: list[Move] = []

    for pile_id, pile in instance.piles.items():
        eligible = _eligible_minerals(instance, pile.group_id)

        for mineral_out in _distinct_minerals(solution, pile_id):
            for mineral_in in eligible:
                if mineral_in != mineral_out:
                    moves.append(((pile_id, mineral_out, mineral_in),))

    return moves


def n2_moves(solution: Solution, instance: ProblemInstance) -> list[Move]:
    """All N2 moves: swap two different minerals between two piles."""

    moves: list[Move] = []
    pile_ids = list(instance.piles)

    for i, pile_a_id in enumerate(pile_ids):
        group_a = instance.piles[pile_a_id].group_id

        for pile_b_id in pile_ids[i + 1:]:
            group_b = instance.piles[pile_b_id].group_id

            for mineral_a in _distinct_minerals(solution, pile_a_id):
                if not instance.minerals[mineral_a].is_eligible(group_b):
                    continue

                for mineral_b in _distinct_minerals(solution, pile_b_id):
                    if mineral_a == mineral_b:
                        continue
                    if not instance.minerals[mineral_b].is_eligible(group_a):
                        continue

                    moves.append(
                        (
                            (pile_a_id, mineral_a, mineral_b),
                            (pile_b_id, mineral_b, mineral_a),
                        )
                    )

    return moves


def n3_moves(solution: Solution, instance: ProblemInstance) -> list[Move]:
    """
    All N3 moves (relocation with chained replacement, D008).

        pile_a: m_x -> m_z
        pile_b: m_y -> m_x

    with m_x, m_y and m_z distinct. The neighborhood is large (order of 10^5
    moves on the example instance), so the local search samples it instead of
    enumerating it (see ``sample_n3_move`` and D014).
    """

    moves: list[Move] = []

    for pile_a_id, pile_a in instance.piles.items():
        eligible_a = _eligible_minerals(instance, pile_a.group_id)

        for pile_b_id, pile_b in instance.piles.items():
            if pile_a_id == pile_b_id:
                continue

            for mineral_x in _distinct_minerals(solution, pile_a_id):
                if not instance.minerals[mineral_x].is_eligible(pile_b.group_id):
                    continue

                for mineral_y in _distinct_minerals(solution, pile_b_id):
                    if mineral_y == mineral_x:
                        continue

                    for mineral_z in eligible_a:
                        if mineral_z in (mineral_x, mineral_y):
                            continue

                        moves.append(
                            (
                                (pile_a_id, mineral_x, mineral_z),
                                (pile_b_id, mineral_y, mineral_x),
                            )
                        )

    return moves


# ---------------------------------------------------------------------------
# Random sampling (used by the shake and by the sampled local search in N3)
# ---------------------------------------------------------------------------

_MAX_SAMPLING_ATTEMPTS = 200


def sample_n1_move(
    solution: Solution,
    instance: ProblemInstance,
    rng: random.Random,
) -> Move | None:
    pile_ids = list(instance.piles)

    for _ in range(_MAX_SAMPLING_ATTEMPTS):
        pile_id = rng.choice(pile_ids)
        group_id = instance.piles[pile_id].group_id
        mineral_out = rng.choice(solution.composition[pile_id])
        candidates = [
            m for m in _eligible_minerals(instance, group_id) if m != mineral_out
        ]
        if candidates:
            return ((pile_id, mineral_out, rng.choice(candidates)),)

    return None


def sample_n2_move(
    solution: Solution,
    instance: ProblemInstance,
    rng: random.Random,
) -> Move | None:
    pile_ids = list(instance.piles)

    for _ in range(_MAX_SAMPLING_ATTEMPTS):
        # Same pile order as n2_moves, so a swap has a single representation.
        index_a, index_b = sorted(rng.sample(range(len(pile_ids)), 2))
        pile_a_id, pile_b_id = pile_ids[index_a], pile_ids[index_b]
        group_a = instance.piles[pile_a_id].group_id
        group_b = instance.piles[pile_b_id].group_id

        mineral_a = rng.choice(solution.composition[pile_a_id])
        mineral_b = rng.choice(solution.composition[pile_b_id])

        if (
            mineral_a != mineral_b
            and instance.minerals[mineral_a].is_eligible(group_b)
            and instance.minerals[mineral_b].is_eligible(group_a)
        ):
            return (
                (pile_a_id, mineral_a, mineral_b),
                (pile_b_id, mineral_b, mineral_a),
            )

    return None


def sample_n3_move(
    solution: Solution,
    instance: ProblemInstance,
    rng: random.Random,
) -> Move | None:
    pile_ids = list(instance.piles)

    for _ in range(_MAX_SAMPLING_ATTEMPTS):
        pile_a_id, pile_b_id = rng.sample(pile_ids, 2)
        group_a = instance.piles[pile_a_id].group_id
        group_b = instance.piles[pile_b_id].group_id

        mineral_x = rng.choice(solution.composition[pile_a_id])
        mineral_y = rng.choice(solution.composition[pile_b_id])

        if mineral_x == mineral_y:
            continue
        if not instance.minerals[mineral_x].is_eligible(group_b):
            continue

        candidates = [
            m
            for m in _eligible_minerals(instance, group_a)
            if m not in (mineral_x, mineral_y)
        ]
        if candidates:
            return (
                (pile_a_id, mineral_x, rng.choice(candidates)),
                (pile_b_id, mineral_y, mineral_x),
            )

    return None


MoveSampler = Callable[[Solution, ProblemInstance, random.Random], "Move | None"]
MoveEnumerator = Callable[[Solution, ProblemInstance], list[Move]]

SAMPLERS: dict[str, MoveSampler] = {
    "N1": sample_n1_move,
    "N2": sample_n2_move,
    "N3": sample_n3_move,
}

ENUMERATORS: dict[str, MoveEnumerator] = {
    "N1": n1_moves,
    "N2": n2_moves,
    "N3": n3_moves,
}


# ---------------------------------------------------------------------------
# Single random neighbor
# ---------------------------------------------------------------------------


def _random_neighbor(
    sampler: MoveSampler,
    solution: Solution,
    instance: ProblemInstance,
    rng: random.Random,
) -> Solution:
    move = sampler(solution, instance, rng)
    if move is None:
        return solution
    return apply_move(solution, move)


def n1_replace(
    solution: Solution,
    instance: ProblemInstance,
    rng: random.Random,
) -> Solution:
    """Replace one truck slot by another eligible mineral."""

    return _random_neighbor(sample_n1_move, solution, instance, rng)


def n2_swap(
    solution: Solution,
    instance: ProblemInstance,
    rng: random.Random,
) -> Solution:
    """Swap two truck slots from different piles while preserving eligibility."""

    return _random_neighbor(sample_n2_move, solution, instance, rng)


def n3_relocate_replace(
    solution: Solution,
    instance: ProblemInstance,
    rng: random.Random,
) -> Solution:
    """
    Relocate one mineral between two piles while introducing another mineral.

        pile_a: m_x -> m_z
        pile_b: m_y -> m_x

    Mass and eligibility are preserved by construction.
    Global mineral usage may change.
    """

    return _random_neighbor(sample_n3_move, solution, instance, rng)

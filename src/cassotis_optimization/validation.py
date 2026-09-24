from __future__ import annotations

from .domain import ProblemInstance


def validate_instance(instance: ProblemInstance) -> list[str]:
    errors: list[str] = []

    for mineral in instance.minerals.values():
        if mineral.min_trucks < 0:
            errors.append(f"{mineral.mineral_id}: min_trucks must be non-negative.")
        if mineral.max_trucks < mineral.min_trucks:
            errors.append(f"{mineral.mineral_id}: max_trucks < min_trucks.")
        if not (mineral.eligible_sinter1 or mineral.eligible_sinter2):
            errors.append(f"{mineral.mineral_id}: mineral is eligible for no group.")

    for group in instance.groups.values():
        if not (group.sio2_min <= group.sio2_target <= group.sio2_max):
            errors.append(f"{group.group_id}: SiO2 target is outside bounds.")
        if not (group.al2o3_min <= group.al2o3_target <= group.al2o3_max):
            errors.append(f"{group.group_id}: Al2O3 target is outside bounds.")
        if group.fet_min > group.fet_max:
            errors.append(f"{group.group_id}: FeT min > max.")

    for pile in instance.piles.values():
        if pile.group_id not in instance.groups:
            errors.append(f"{pile.pile_id}: unknown group {pile.group_id}.")
        try:
            _ = pile.n_trucks
        except ValueError as exc:
            errors.append(str(exc))

    required_trucks = sum(pile.n_trucks for pile in instance.piles.values())
    max_available = sum(mineral.max_trucks for mineral in instance.minerals.values())
    min_required = sum(mineral.min_trucks for mineral in instance.minerals.values())

    if max_available < required_trucks:
        errors.append(
            f"Total maximum availability ({max_available}) is below required trucks "
            f"({required_trucks})."
        )
    if min_required > required_trucks:
        errors.append(
            f"Total minimum usage ({min_required}) exceeds required trucks "
            f"({required_trucks})."
        )

    return errors

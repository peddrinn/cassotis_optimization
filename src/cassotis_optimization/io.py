from __future__ import annotations

import csv
from pathlib import Path

from .domain import GroupSpec, Mineral, Pile, ProblemInstance


def _as_bool(value: str) -> bool:
    return value.strip() in {"1", "true", "True", "yes", "YES"}


def load_instance(directory: str | Path) -> ProblemInstance:
    directory = Path(directory)

    minerals: dict[str, Mineral] = {}
    with (directory / "minerals.csv").open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            mineral = Mineral(
                mineral_id=row["mineral_id"],
                price_rs_per_t=float(row["price_rs_per_t"]),
                fet_pct=float(row["fet_pct"]),
                sio2_pct=float(row["sio2_pct"]),
                al2o3_pct=float(row["al2o3_pct"]),
                min_trucks=int(row["min_trucks"]),
                max_trucks=int(row["max_trucks"]),
                eligible_sinter1=_as_bool(row["eligible_sinter1"]),
                eligible_sinter2=_as_bool(row["eligible_sinter2"]),
            )
            minerals[mineral.mineral_id] = mineral

    groups: dict[str, GroupSpec] = {}
    with (directory / "groups.csv").open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            group = GroupSpec(
                group_id=row["group_id"],
                fet_min=float(row["fet_min"]),
                fet_target=float(row["fet_target"]) if row["fet_target"] else None,
                fet_max=float(row["fet_max"]),
                sio2_min=float(row["sio2_min"]),
                sio2_target=float(row["sio2_target"]),
                sio2_max=float(row["sio2_max"]),
                al2o3_min=float(row["al2o3_min"]),
                al2o3_target=float(row["al2o3_target"]),
                al2o3_max=float(row["al2o3_max"]),
            )
            groups[group.group_id] = group

    piles: dict[str, Pile] = {}
    with (directory / "piles.csv").open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            pile = Pile(
                pile_id=row["pile_id"],
                group_id=row["group_id"],
                mass_kt=float(row["mass_kt"]),
            )
            piles[pile.pile_id] = pile

    return ProblemInstance(minerals=minerals, groups=groups, piles=piles)

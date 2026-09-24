from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .domain import ProblemInstance


@dataclass(frozen=True)
class Solution:
    """A pile composition represented by one mineral id per truck slot."""

    composition: dict[str, tuple[str, ...]]

    def counts_by_pile(self) -> dict[str, Counter[str]]:
        return {
            pile_id: Counter(mineral_ids)
            for pile_id, mineral_ids in self.composition.items()
        }

    def total_usage(self, instance: ProblemInstance) -> dict[str, int]:
        usage = {mineral_id: 0 for mineral_id in instance.minerals}
        for counts in self.counts_by_pile().values():
            for mineral_id, count in counts.items():
                usage[mineral_id] += count
        return usage

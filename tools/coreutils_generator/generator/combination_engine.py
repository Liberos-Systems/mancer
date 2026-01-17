"""Engine generating option sets in tiered arrangement."""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class CombinationSettings:
    """Quantitative limits for combination generation."""

    tier0_single_limit: int = 8
    tier2_pairwise_limit: int = 120
    tier4_full_limit: int = 200
    max_full_option_depth: int = 4


@dataclass(frozen=True)
class CombinationCase:
    """Description of generated option set."""

    options: tuple[str, ...]
    tier: str


class CombinationEngine:
    """Implementation of combinatorial strategies."""

    def __init__(self, settings: CombinationSettings | None = None):
        self._settings = settings or CombinationSettings()

    def generate(
        self,
        available_options: Sequence[str],
        popular_sets: Sequence[Sequence[str]],
        tiers: Sequence[str],
        max_full_options: int,
        tier2_options: Sequence[str] | None = None,
    ) -> list[CombinationCase]:
        normalized_options = list(dict.fromkeys(available_options))
        normalized_tier2 = (
            list(dict.fromkeys(tier2_options)) if tier2_options is not None else normalized_options
        )
        cases: list[CombinationCase] = []
        if "tier0" in tiers:
            cases.extend(self._generate_tier0(normalized_options))
        if "tier1" in tiers:
            cases.extend(self._generate_tier1(popular_sets))
        if "tier2" in tiers:
            cases.extend(self._generate_tier2(normalized_tier2))
        if "tier4" in tiers:
            depth = min(max_full_options, self._settings.max_full_option_depth)
            cases.extend(self._generate_tier4(normalized_options, depth))
        return cases

    def _generate_tier0(self, options: Sequence[str]) -> list[CombinationCase]:
        limit = self._settings.tier0_single_limit
        single_options = [CombinationCase(options=(opt,), tier="tier0") for opt in options[:limit]]
        return [CombinationCase(options=(), tier="tier0"), *single_options]

    def _generate_tier1(self, popular_sets: Sequence[Sequence[str]]) -> list[CombinationCase]:
        cases = []
        for option_set in popular_sets:
            canonical = tuple(dict.fromkeys(option_set))
            if not canonical:
                continue
            cases.append(CombinationCase(options=canonical, tier="tier1"))
        return cases

    def _generate_tier2(self, options: Sequence[str]) -> list[CombinationCase]:
        combos = itertools.combinations(options, 2)
        limited = itertools.islice(combos, self._settings.tier2_pairwise_limit)
        return [CombinationCase(options=tuple(combo), tier="tier2") for combo in limited]

    def _generate_tier4(self, options: Sequence[str], max_depth: int) -> list[CombinationCase]:
        cases: list[CombinationCase] = []
        remaining = self._settings.tier4_full_limit
        for depth in range(3, max_depth + 1):
            for combo in itertools.combinations(options, depth):
                cases.append(CombinationCase(options=combo, tier="tier4"))
                remaining -= 1
                if remaining <= 0:
                    return cases
        return cases



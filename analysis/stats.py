from __future__ import annotations

from collections import Counter
from statistics import mean


def summarize_steps(steps: list[int]) -> dict[str, float | int]:
    return {
        "count": len(steps),
        "min": min(steps) if steps else 0,
        "max": max(steps) if steps else 0,
        "avg": mean(steps) if steps else 0.0,
    }


def distribution(steps: list[int]) -> dict[int, int]:
    return dict(sorted(Counter(steps).items()))

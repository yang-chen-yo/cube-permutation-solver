from __future__ import annotations

import csv
from pathlib import Path

from analysis.stats import summarize_steps
from src.core import Cube, State
from src.utils import parse_permutation


SELECTED_4D_PERMUTATIONS = [
    "15,0,10,4,3,11,1,7,8,5,6,2,12,9,14,13",
    "0,8,1,12,2,5,9,14,4,6,10,7,3,11,13,15",
    "1,5,0,8,9,11,2,15,3,12,4,6,10,14,13,7",
    "1,9,0,4,10,8,2,11,3,15,5,12,7,14,13,6",
    "3,1,7,13,11,0,8,15,2,5,10,6,9,14,12,4",
    "3,1,11,7,8,0,9,5,2,6,15,13,14,4,10,12",
    "3,5,11,1,8,0,9,7,2,6,14,13,10,4,12,15",
    "0,1,2,3,4,5,6,8,7,9,10,11,12,13,14,15",
    "6,2,14,13,3,11,10,7,0,5,8,1,15,12,4,9",
    "6,4,11,0,9,8,12,2,15,5,3,7,10,13,14,1",
    "13,1,14,0,9,2,15,6,12,8,11,3,4,5,7,10",
    "0,2,3,5,7,11,13,1,4,6,8,9,10,12,14,15",
    "8,14,0,3,2,5,10,7,4,9,12,11,1,13,6,15",
    "7,14,9,6,11,0,13,2,5,15,10,12,1,4,3,8",
    "1,2,4,8,0,3,5,6,7,9,10,11,12,13,14,15",
    "0,1,14,3,4,5,7,8,15,13,10,6,9,12,11,2",
    "2,5,3,15,4,13,6,7,8,9,10,11,12,1,14,0",
    "0,1,2,3,4,5,14,11,8,6,10,9,12,15,13,7",
    "1,2,3,4,5,6,7,8,9,0,10,11,12,13,14,15",
    "11,3,9,2,7,13,15,14,8,1,4,10,0,12,6,5",
    "6,0,12,15,7,1,5,2,4,10,13,3,11,8,14,9",
    "9,0,2,15,11,6,7,8,14,3,4,13,5,1,12,10",
    "6,15,9,5,13,12,3,7,2,10,1,11,0,14,4,8",
    "11,3,9,2,7,13,15,14,8,1,4,10,0,12,6,5",
    "15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0",
]


def run_4d(algorithm_instances: dict[str, object], output_csv: Path):
    _ = Cube(dimension=4)
    states = [parse_permutation(text) for text in SELECTED_4D_PERMUTATIONS]

    rows = []
    step_map: dict[str, list[int]] = {name: [] for name in algorithm_instances}

    for state in states:
        row = {"state": " ".join(map(str, state))}
        for name, router in algorithm_instances.items():
            if name == "bfs":
                try:
                    steps = len(router.route(state))
                except RuntimeError:
                    steps = -1
            else:
                steps = len(router.route(state))
            row[name] = steps
            step_map[name].append(steps)
        rows.append(row)

    with output_csv.open("w", newline="", encoding="utf-8") as fh:
        fieldnames = ["state", *algorithm_instances.keys()]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    cleaned = {
        name: [s for s in values if s >= 0]
        for name, values in step_map.items()
    }
    summary = {name: summarize_steps(values) for name, values in cleaned.items()}
    return rows, step_map, summary

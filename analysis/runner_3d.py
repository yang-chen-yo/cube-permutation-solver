from __future__ import annotations

import csv
from itertools import permutations
from pathlib import Path

from analysis.stats import summarize_steps
from src.core import Cube, State


def run_3d(algorithm_instances: dict[str, object], output_csv: Path):
    cube = Cube(dimension=3)
    states = [tuple(p) for p in permutations(range(cube.size))]

    rows = []
    step_map: dict[str, list[int]] = {name: [] for name in algorithm_instances}

    bfs_router = algorithm_instances.get("bfs")
    bfs_distances = bfs_router.all_distances() if bfs_router else {}

    for state in states:
        row = {"state": " ".join(map(str, state))}
        for name, router in algorithm_instances.items():
            if name == "bfs":
                steps = bfs_distances[state]
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

    summary = {name: summarize_steps(values) for name, values in step_map.items()}
    return rows, step_map, summary

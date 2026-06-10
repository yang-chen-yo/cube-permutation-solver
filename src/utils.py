from __future__ import annotations

import importlib
import inspect
import itertools
import pkgutil
from pathlib import Path

from .base import RouterAlgorithm
from .core import Cube, Edge, Matching, State


def generate_all_states(cube: Cube):
    return itertools.permutations(range(cube.size))


def generate_dimension_matchings(cube: Cube) -> list[Matching]:
    matchings: list[Matching] = []
    for bit in range(cube.dimension):
        matching: Matching = []
        seen: set[int] = set()
        for v in range(cube.size):
            u = v ^ (1 << bit)
            if v < u and v not in seen and u not in seen:
                matching.append((v, u))
                seen.add(v)
                seen.add(u)
        matchings.append(matching)
    return matchings


def generate_all_matchings(cube: Cube) -> list[Matching]:
    edges = cube.edges
    matchings: list[Matching] = [[]]

    def backtrack(index: int, current: Matching, used: set[int]):
        if index >= len(edges):
            if current:
                matchings.append(current.copy())
            return

        a, b = edges[index]
        backtrack(index + 1, current, used)
        if a not in used and b not in used:
            used.add(a)
            used.add(b)
            current.append((a, b))
            backtrack(index + 1, current, used)
            current.pop()
            used.remove(a)
            used.remove(b)

    backtrack(0, [], set())
    return matchings


def parse_permutation(text: str) -> State:
    return tuple(int(x.strip()) for x in text.split(",") if x.strip())


def load_algorithms(enabled: set[str] | None = None) -> dict[str, type[RouterAlgorithm]]:
    package_name = "src.algorithms"
    package = importlib.import_module(package_name)
    discovered: dict[str, type[RouterAlgorithm]] = {}

    for module_info in pkgutil.iter_modules(package.__path__):
        if module_info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{package_name}.{module_info.name}")
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls is RouterAlgorithm or not issubclass(cls, RouterAlgorithm):
                continue
            key = getattr(cls, "NAME", cls.__name__.lower())
            if enabled is None or key in enabled:
                discovered[key] = cls

    return dict(sorted(discovered.items()))


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

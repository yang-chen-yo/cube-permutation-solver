from __future__ import annotations

from dataclasses import dataclass

State = tuple[int, ...]
Edge = tuple[int, int]
Matching = list[Edge]


@dataclass(frozen=True)
class Cube:
    dimension: int

    @property
    def size(self) -> int:
        return 1 << self.dimension

    @property
    def identity(self) -> State:
        return tuple(range(self.size))

    @property
    def edges(self) -> list[Edge]:
        edges: list[Edge] = []
        for v in range(self.size):
            for bit in range(self.dimension):
                u = v ^ (1 << bit)
                if v < u:
                    edges.append((v, u))
        return edges

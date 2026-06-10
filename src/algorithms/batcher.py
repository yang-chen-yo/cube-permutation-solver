from __future__ import annotations

from src.base import RouterAlgorithm
from src.core import Matching, State


class BatcherRouter(RouterAlgorithm):
    NAME = "batcher"

    def __init__(self, cube):
        super().__init__(cube)
        self.network = self._build_network(cube.size)

    def _build_network(self, n: int) -> list[list[tuple[int, int]]]:
        layers: list[list[tuple[int, int]]] = []
        k = 2
        while k <= n:
            j = k // 2
            while j > 0:
                layer: list[tuple[int, int]] = []
                for i in range(n):
                    ixj = i ^ j
                    if ixj > i:
                        if (i & k) == 0:
                            layer.append((i, ixj))
                        else:
                            layer.append((ixj, i))
                if layer:
                    # deduplicate while keeping order
                    seen = set()
                    cleaned = []
                    for a, b in layer:
                        edge = (min(a, b), max(a, b))
                        if edge in seen:
                            continue
                        seen.add(edge)
                        cleaned.append((a, b))
                    layers.append(cleaned)
                j //= 2
            k *= 2
        return layers

    def route(self, start_state: State) -> list[Matching]:
        state = list(start_state)
        path: list[Matching] = []
        for layer in self.network:
            move: Matching = []
            for a, b in layer:
                if state[a] > state[b]:
                    state[a], state[b] = state[b], state[a]
                    move.append((a, b))
            if move:
                path.append(move)
        return path

from __future__ import annotations

from src.base import RouterAlgorithm
from src.core import Matching, State
from src.utils import generate_dimension_matchings


class CustomRouter(RouterAlgorithm):
    NAME = "custom"

    def __init__(self, cube):
        super().__init__(cube)
        self.dimension_matchings = generate_dimension_matchings(cube)

    def route(self, start_state: State) -> list[Matching]:
        state = start_state
        path: list[Matching] = []

        # Greedy local-improvement rounds over each dimension matching.
        for _ in range(self.cube.size * 4):
            if self.is_goal(state):
                break
            improved = False
            for matching in self.dimension_matchings:
                move = self._best_subset_move(state, matching)
                if not move:
                    continue
                next_state = self.apply_move(state, move)
                if self._score(next_state) < self._score(state):
                    path.append(move)
                    state = next_state
                    improved = True
            if not improved:
                break

        if not self.is_goal(state):
            # Deterministic fallback: place each value by edge-path bubbling.
            path.extend(self._finish_by_edge_bubbling(state))
        return path

    def _score(self, state: State) -> int:
        return sum(1 for idx, value in enumerate(state) if idx != value)

    def _best_subset_move(self, state: State, matching: Matching) -> Matching:
        best: Matching = []
        best_gain = 0
        for edge in matching:
            trial = [edge]
            gain = self._score(state) - self._score(self.apply_move(state, trial))
            if gain > best_gain:
                best = trial
                best_gain = gain
        return best

    def _finish_by_edge_bubbling(self, state: State) -> list[Matching]:
        path: list[Matching] = []
        current = state
        adjacency: dict[int, list[int]] = {i: [] for i in range(self.cube.size)}
        for a, b in self.cube.edges:
            adjacency[a].append(b)
            adjacency[b].append(a)

        for target_pos in range(self.cube.size):
            if current[target_pos] == target_pos:
                continue
            src = current.index(target_pos)
            # BFS on cube graph to move value to target_pos
            queue = [src]
            parent = {src: None}
            found = False
            while queue and not found:
                node = queue.pop(0)
                if node == target_pos:
                    found = True
                    break
                for nxt in adjacency[node]:
                    if nxt not in parent:
                        parent[nxt] = node
                        queue.append(nxt)
            if not found:
                continue
            route_nodes = []
            n = target_pos
            while parent[n] is not None:
                p = parent[n]
                route_nodes.append((p, n))
                n = p
            route_nodes.reverse()
            for edge in route_nodes:
                move = [edge]
                current = self.apply_move(current, move)
                path.append(move)
        return path

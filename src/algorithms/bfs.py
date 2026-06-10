from __future__ import annotations

from collections import deque

from src.base import RouterAlgorithm
from src.core import Matching, State
from src.utils import generate_all_matchings


class BFSRouter(RouterAlgorithm):
    NAME = "bfs"

    def __init__(self, cube, use_matchings: bool = True, max_visited: int | None = None):
        super().__init__(cube)
        self.use_matchings = use_matchings
        self.max_visited = max_visited
        self.moves = self._build_moves()

    def _build_moves(self) -> list[Matching]:
        if self.use_matchings:
            return generate_all_matchings(cube=self.cube)
        return [[edge] for edge in self.cube.edges]

    def route(self, start_state: State) -> list[Matching]:
        goal_state = self.goal_state
        if start_state == goal_state:
            return []

        queue = deque([start_state])
        parent: dict[State, State | None] = {start_state: None}
        parent_move: dict[State, Matching] = {}

        while queue:
            state = queue.popleft()
            for move in self.moves:
                next_state = self.apply_move(state, move)
                if next_state in parent:
                    continue
                parent[next_state] = state
                parent_move[next_state] = move
                if next_state == goal_state:
                    return self._reconstruct_path(parent, parent_move, next_state)
                if self.max_visited is not None and len(parent) >= self.max_visited:
                    raise RuntimeError("BFS visit limit reached")
                queue.append(next_state)

        raise ValueError(f"No route found from {start_state}")

    def all_distances(self) -> dict[State, int]:
        goal_state = self.goal_state
        queue = deque([goal_state])
        distance: dict[State, int] = {goal_state: 0}

        while queue:
            state = queue.popleft()
            for move in self.moves:
                next_state = self.apply_move(state, move)
                if next_state in distance:
                    continue
                distance[next_state] = distance[state] + 1
                queue.append(next_state)
        return distance

    @staticmethod
    def _reconstruct_path(
        parent: dict[State, State | None],
        parent_move: dict[State, Matching],
        state: State,
    ) -> list[Matching]:
        path: list[Matching] = []
        while parent[state] is not None:
            path.append(parent_move[state])
            state = parent[state]
        path.reverse()
        return path

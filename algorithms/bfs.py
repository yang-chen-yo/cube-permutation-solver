from collections import deque

from utils import Matching, State, generate_all_matchings

from .base import RoutingAlgorithm


class BFSRouter(RoutingAlgorithm):
    """
    Exact shortest-path router over the permutation state graph.

    This BFS is not searching inside the hypercube from one vertex to another.
    Instead, each BFS node is a complete permutation state, and each BFS edge is
    one legal routing step. Therefore, the depth returned by BFS is exactly the
    minimum number of routing steps under the chosen move model.

    By default, one BFS step is one matching-swap round, so multiple
    non-overlapping edges may be swapped in parallel. Set
    ``use_matchings=False`` to make one BFS step swap exactly one edge.
    """

    def __init__(self, cube, use_matchings: bool = False):
        super().__init__(cube)
        self.use_matchings = use_matchings
        self.moves = self._build_moves()

    def _build_moves(self) -> list[Matching]:
        """
        Build the legal move set used by BFS.

        Matching mode is the model emphasized by the assignment: one step may
        include several independent edge swaps. Single-edge mode is kept only
        for comparison with groups that count one edge swap as one step.
        """
        if self.use_matchings:
            return generate_all_matchings(cube=self.cube)

        return [[edge] for edge in self.cube.edges]

    def route(self, start_state: State) -> list[Matching]:
        """
        Return one shortest sequence of moves from ``start_state`` to identity.

        Each item in the returned path is one BFS step. In matching mode, a step
        may contain multiple non-overlapping edges; in single-edge mode, every
        step contains exactly one edge.
        """
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

                # The first time BFS reaches a state is always through a
                # shortest path, so we store only one parent pointer.
                parent[next_state] = state
                parent_move[next_state] = move

                if self.is_goal(next_state):
                    return self._reconstruct_path(parent, parent_move, next_state)

                queue.append(next_state)

        raise ValueError(f"No route found from {start_state}")

    def all_distances(self) -> dict[State, int]:
        """
        Compute the shortest routing steps from every state to the identity state.

        The returned dictionary maps each permutation state to its BFS
        distance: the minimum number of steps needed to route that state back
        to the identity state ``(0, 1, ..., N - 1)``.

        For example, ``distance[(1, 0, 2, 3, 4, 5, 6, 7)] == 1`` because one
        move ``[(0, 1)]`` fixes that permutation.

        Matching swaps are reversible, so one BFS starting from the identity
        state gives the shortest distance for every permutation state.
        """
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
        """Follow parent pointers backwards and return the path in route order."""
        path: list[Matching] = []

        while parent[state] is not None:
            path.append(parent_move[state])
            state = parent[state]

        path.reverse()
        return path

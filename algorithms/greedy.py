from utils import Edge, Matching, State

from .base import RoutingAlgorithm


class GreedyMatchingRouter(RoutingAlgorithm):
    """
    Custom routing algorithm: greedy matching with beam-search fallback.

    The main idea is to move packets along dimensions where their current
    vertex differs from their destination. If several packets can move through
    non-overlapping edges, they are swapped in parallel as one matching step.

    Pure greedy routing can cycle or get stuck because locally good moves may
    block each other. When that happens, this router switches to a beam-search
    fallback that keeps several promising partial paths instead of only one.
    """

    total_cases = 0
    total_steps = 0

    def __init__(self, cube, max_steps: int = 1_000, beam_width: int = 500):
        super().__init__(cube)
        self.max_steps = max_steps
        self.beam_width = beam_width

    def route(self, start_state: State) -> list[Matching]:
        """
        Route ``start_state`` to identity.

        Returns:
            A list of matching-swap steps. The length of the list is the step
            count reported in the experiment CSV files.
        """
        if self.is_goal(start_state):
            return []

        state = start_state
        path: list[Matching] = []
        seen_states = {state}

        for _ in range(self.max_steps):
            matching = self._choose_matching(state, seen_states)
            if not matching:
                # Greedy has no safe progress move; allow the fallback to take
                # temporary detours.
                return path + self._beam_search(state)

            state = self.apply_valid_move(state, matching)
            path.append(matching)

            if self.is_goal(state):

                GreedyMatchingRouter.total_cases += 1
                GreedyMatchingRouter.total_steps += len(path)

                if GreedyMatchingRouter.total_cases % 1000 == 0:

                    avg = (
                        GreedyMatchingRouter.total_steps
                        / GreedyMatchingRouter.total_cases
                    )

                    print(
                        f"[{GreedyMatchingRouter.total_cases}] "
                        f"avg={avg:.4f}"
                    )

                return path
            seen_states.add(state)
        return self._beam_search(start_state)

    def _beam_search(self, start_state: State) -> list[Matching]:
        """
        Search for a route while keeping only the best few partial paths.

        This fallback allows temporary detours. Each beam move swaps one edge,
        so the branching factor stays small enough for selected 4D cases.
        """
        beam: list[tuple[State, list[Matching]]] = [(start_state, [])]
        visited_depth = {start_state: 0}

        for depth in range(1, self.max_steps + 1):
            candidates: list[tuple[tuple[int, int], State, list[Matching]]] = []

            for state, path in beam:
                for move in self._beam_moves():
                    next_state = self.apply_move(state, move)

                    if visited_depth.get(next_state, self.max_steps + 1) <= depth:
                        continue

                    next_path = path + [move]
                    if self.is_goal(next_state):
                        return next_path

                    visited_depth[next_state] = depth
                    candidates.append((self._state_score(next_state), next_state, next_path))

            if not candidates:
                break

            candidates.sort(key=lambda candidate: candidate[0])
            beam = [
                (state, path)
                for _, state, path in candidates[: self.beam_width]
            ]

        raise ValueError("Beam search router got stuck")

    def _beam_moves(self) -> list[Matching]:
        """Return single-edge moves used by beam search to limit branching."""
        return [[edge] for edge in self.cube.edges]

    def _state_score(self, state: State) -> tuple[int, int]:
        """
        Score a state for beam search.

        Lower is better. Total Hamming distance measures how far all packets
        are from their destinations; misplaced count breaks ties.
        """
        return (
            self._total_hamming_distance(state),
            self._misplaced_packet_count(state),
        )

    def _choose_matching(
        self, state: State, seen_states: set[State] | None = None
    ) -> Matching:

        candidates = self._candidate_edges(state)

        best_matching: Matching = []
        best_gain = -1
        best_score = (-1, 0)
        best_matching = []

        current_hd = self._total_hamming_distance(state)

        for start_index in range(len(candidates)):
            used_vertices = set()
            matching: Matching = []

            ordered_candidates = (
                candidates[start_index:]
                + candidates[:start_index]
            )

            for _, _, edge in ordered_candidates:
                if edge[0] in used_vertices:
                    continue

                if edge[1] in used_vertices:
                    continue

                matching.append(edge)

                used_vertices.add(edge[0])
                used_vertices.add(edge[1])

            if not matching:
                continue

            next_state = self.apply_move(state, matching)

            if seen_states is not None and next_state in seen_states:
                continue

            next_hd = self._total_hamming_distance(next_state)

            gain = current_hd - next_hd

            # if gain > best_gain:
            #     best_gain = gain
            #     best_matching = matching
            score = (
                gain,
                -self._misplaced_packet_count(next_state)
            )

            if score > best_score:
                best_score = score
                best_matching = matching

        return best_matching

    def _candidate_edges(self, state: State) -> list[tuple[int, int, Edge]]:
        """
        List greedy edge proposals.

        Each proposal is an edge that would reduce one packet's Hamming
        distance to its destination. More distant packets are prioritized first
        so hard-to-place packets get earlier access to conflict-free edges.
        """
        candidates = []

        for vertex in range(self.cube.N):
            destination = state[vertex]
            if vertex == destination:
                continue

            priority = self._hamming_distance(vertex, destination)
            for edge in self._candidate_edges_for_vertex(vertex, state):
                candidates.append((-priority, vertex, edge))

        candidates.sort()
        return candidates

    def _candidate_edge_for_vertex(self, vertex: int, state: State) -> Edge | None:
        """
        Return one edge that moves the packet at ``vertex`` closer to its destination.

        If the packet is already at its destination, return None.
        """
        destination = state[vertex]
        if vertex == destination:
            return None

        for bit in range(self.cube.dim):
            if (vertex ^ destination) & (1 << bit):
                neighbor = vertex ^ (1 << bit)
                return self.normalize_edge(vertex, neighbor)

        return None

    def _candidate_edges_for_vertex(self, vertex: int, state: State) -> list[Edge]:
        """Return all edges that move the packet at ``vertex`` closer to its destination."""
        destination = state[vertex]
        edges = []

        for bit in range(self.cube.dim):
            if (vertex ^ destination) & (1 << bit):
                neighbor = vertex ^ (1 << bit)
                edges.append(self.normalize_edge(vertex, neighbor))

        return edges

    def _hamming_distance(self, u: int, v: int) -> int:
        """Return the number of different bits between two vertices."""
        return (u ^ v).bit_count()

    def _total_hamming_distance(self, state: State) -> int:
        """Return the sum of packet-to-destination Hamming distances."""
        return sum(
            self._hamming_distance(vertex, destination)
            for vertex, destination in enumerate(state)
        )

    def _misplaced_packet_count(self, state: State) -> int:
        """Return how many packets are not yet at their destination vertex."""
        return sum(vertex != destination for vertex, destination in enumerate(state))


  
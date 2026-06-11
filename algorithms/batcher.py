from functools import cache

from utils import Edge, Matching, State

from .base import RoutingAlgorithm


class BatcherRouter(RoutingAlgorithm):
    """
    Parallel Batcher odd-even mergesort baseline.

    The sorting network gives compare-exchange pairs over array positions. A
    compare-exchange between non-adjacent hypercube vertices is implemented as
    a sequence of legal edge swaps along a shortest hypercube path.

    Independent comparators in the same sorting-network layer are executed in
    parallel when their complete hypercube paths do not share vertices.
    """

    def route(self, start_state: State) -> list[Matching]:
        """
        Sort packet labels into identity order using Batcher comparators.

        Since ``state[i]`` is the destination label at vertex ``i``, sorting the
        labels into ascending order gives the identity state. Each returned step
        is a valid matching and may contain multiple parallel edge swaps.
        """
        state = start_state
        path: list[Matching] = []

        for layer in self._comparator_layers(self.cube.N):
            swap_sequences = [
                self._swap_vertices_via_path(u, v)
                for u, v in layer
                if state[u] > state[v]
            ]

            for group in self._group_disjoint_paths(swap_sequences):
                for matching in self._parallel_steps(group):
                    state = self.apply_valid_move(state, matching)
                    path.append(matching)

        if not self.is_goal(state):
            raise ValueError(f"Batcher router failed to sort state: {state}")

        return path

    @cache
    def _comparator_layers(self, n: int) -> tuple[tuple[Edge, ...], ...]:
        """
        Group comparators into the earliest valid sorting-network layers.

        Comparators in one layer never share endpoints. Comparator order on
        every array position remains the same as in the original Batcher
        network.
        """
        layers: list[list[Edge]] = []
        last_layer = [-1] * n

        for u, v in self._comparators(n):
            layer_index = max(last_layer[u], last_layer[v]) + 1

            while len(layers) <= layer_index:
                layers.append([])

            layers[layer_index].append((u, v))
            last_layer[u] = layer_index
            last_layer[v] = layer_index

        return tuple(tuple(layer) for layer in layers)

    @cache
    def _comparators(self, n: int) -> tuple[Edge, ...]:
        """
        Build the Batcher odd-even mergesort comparator sequence.

        The returned pairs are array indices, not necessarily hypercube edges.
        ``route`` later converts non-edge comparators into legal path swaps.
        """
        comparators: list[Edge] = []

        def odd_even_merge_sort(lo: int, length: int) -> None:
            if length <= 1:
                return

            half = length // 2
            odd_even_merge_sort(lo, half)
            odd_even_merge_sort(lo + half, half)
            odd_even_merge(lo, length, 1)

        def odd_even_merge(lo: int, length: int, stride: int) -> None:
            step = stride * 2
            if step < length:
                odd_even_merge(lo, length, step)
                odd_even_merge(lo + stride, length, step)

                for index in range(lo + stride, lo + length - stride, step):
                    comparators.append((index, index + stride))
            else:
                comparators.append((lo, lo + stride))

        odd_even_merge_sort(0, n)
        return tuple(comparators)

    def _swap_vertices_via_path(self, source: int, target: int) -> list[Edge]:
        """
        Return edge swaps that transpose two vertices along a hypercube path.

        For path a-b-c-d, the sequence ab, bc, cd, bc, ab swaps the values at
        a and d while restoring the intermediate vertices.
        """
        vertex_path = self._shortest_vertex_path(source, target)
        forward_edges = [
            self.normalize_edge(u, v)
            for u, v in zip(vertex_path, vertex_path[1:])
        ]
        backward_edges = forward_edges[-2::-1]

        return forward_edges + backward_edges

    @staticmethod
    def _group_disjoint_paths(
        swap_sequences: list[list[Edge]],
    ) -> list[list[list[Edge]]]:
        """
        Greedily group endpoint swaps whose complete paths are vertex-disjoint.

        A complete endpoint swap must preserve its edge order. Vertex-disjoint
        paths can safely advance together without interfering with each other.
        """
        groups: list[list[list[Edge]]] = []
        group_vertices: list[set[int]] = []

        for sequence in swap_sequences:
            vertices = {vertex for edge in sequence for vertex in edge}

            for index, used_vertices in enumerate(group_vertices):
                if vertices.isdisjoint(used_vertices):
                    groups[index].append(sequence)
                    used_vertices.update(vertices)
                    break
            else:
                groups.append([sequence])
                group_vertices.append(vertices)

        return groups

    @staticmethod
    def _parallel_steps(group: list[list[Edge]]) -> list[Matching]:
        """Combine equal-time edges from vertex-disjoint swap sequences."""
        if not group:
            return []

        return [
            [
                sequence[step]
                for sequence in group
                if step < len(sequence)
            ]
            for step in range(max(len(sequence) for sequence in group))
        ]

    def _shortest_vertex_path(self, source: int, target: int) -> list[int]:
        """
        Return one shortest hypercube path from ``source`` to ``target``.

        The path flips differing bits in increasing dimension order. Any order
        of differing bits would still be shortest; this fixed order keeps
        results deterministic.
        """
        path = [source]
        current = source

        for bit in range(self.cube.dim):
            if (current ^ target) & (1 << bit):
                current ^= 1 << bit
                path.append(current)

        return path

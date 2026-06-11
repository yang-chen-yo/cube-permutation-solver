# algorithms/batcher.py
from functools import cache
from utils import Edge, Matching, State
from .base import RoutingAlgorithm

class BatcherRouter(RoutingAlgorithm):
    """
    老師課堂教授的標準 Batcher Odd-Even Mergesort。
    特徵：會產生長距離的跨節點配對，依賴 _swap_vertices_via_path 進行繞路交換。
    """
    def __init__(self, cube, use_parallel: bool = True):
        super().__init__(cube)
        self.use_parallel = use_parallel

    def route(self, start_state: State) -> list[Matching]:
        state = start_state
        path: list[Matching] = []

        for layer in self._comparator_layers(self.cube.N):
            swap_sequences = [
                self._swap_vertices_via_path(u, v)
                for u, v in layer
                if state[u] > state[v]
            ]

            if self.use_parallel:
                for group in self._group_disjoint_paths(swap_sequences):
                    for matching in self._parallel_steps(group):
                        state = self.apply_valid_move(state, matching)
                        path.append(matching)
            else:
                for sequence in swap_sequences:
                    for edge in sequence:
                        matching = [edge]
                        state = self.apply_valid_move(state, matching)
                        path.append(matching)

        if not self.is_goal(state):
            raise ValueError(f"Batcher router failed to sort state: {state}")

        return path

    @cache
    def _comparator_layers(self, n: int) -> tuple[tuple[Edge, ...], ...]:
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
        comparators: list[Edge] = []
        def odd_even_merge_sort(lo: int, length: int) -> None:
            if length <= 1: return
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
        vertex_path = self._shortest_vertex_path(source, target)
        forward_edges = [self.normalize_edge(u, v) for u, v in zip(vertex_path, vertex_path[1:])]
        backward_edges = forward_edges[-2::-1]
        return forward_edges + backward_edges

    @staticmethod
    def _group_disjoint_paths(swap_sequences: list[list[Edge]]) -> list[list[list[Edge]]]:
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
        if not group: return []
        return [
            [sequence[step] for sequence in group if step < len(sequence)]
            for step in range(max(len(sequence) for sequence in group))
        ]

    def _shortest_vertex_path(self, source: int, target: int) -> list[int]:
        path = [source]
        current = source
        for bit in range(self.cube.dim):
            if (current ^ target) & (1 << bit):
                current ^= 1 << bit
                path.append(current)
        return path
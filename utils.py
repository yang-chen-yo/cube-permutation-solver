# utils.py
from itertools import combinations
from typing import TypeAlias

State: TypeAlias = tuple[int, ...]
Edge: TypeAlias = tuple[int, int]
Matching: TypeAlias = list[Edge]

class Cube:
    def __init__(self, dim: int):
        self.dim = dim
        self.N = 1 << dim
        self.edges = self._build_edges()

    def _build_edges(self) -> list[Edge]:
        """產生超立方體所有合法的物理邊 (小索引在前)"""
        edges = []
        for u in range(self.N):
            for d in range(self.dim):
                v = u ^ (1 << d)
                if u < v:
                    edges.append((u, v))
        return edges

def generate_all_matchings(cube: Cube) -> list[Matching]:
    """
    產生超立方體上所有合法的獨立邊集合 (Matchings)，包含空集合與單邊。
    透過回溯法 (Backtracking) 找出所有互不相交的邊組合。
    """
    all_matchings: list[Matching] = [[]]
    edges = cube.edges

    def backtrack(start_idx: int, current_matching: Matching, used_vertices: set[int]):
        if current_matching:
            all_matchings.append(list(current_matching))
        
        for i in range(start_idx, len(edges)):
            u, v = edges[i]
            if u not in used_vertices and v not in used_vertices:
                used_vertices.add(u)
                used_vertices.add(v)
                current_matching.append((u, v))
                
                backtrack(i + 1, current_matching, used_vertices)
                
                current_matching.pop()
                used_vertices.remove(u)
                used_vertices.remove(v)

    backtrack(0, [], set())
    return all_matchings
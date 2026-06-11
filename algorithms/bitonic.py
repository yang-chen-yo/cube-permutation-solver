# algorithms/bitonic.py
from utils import Matching, State
from .base import RoutingAlgorithm

class BitonicRouter(RoutingAlgorithm):
    """
    超立方體完美適配版：Batcher Bitonic Sort。
    特徵：利用位元運算，確保每一次交換的點 Hamming Distance 永遠為 1 (實體相鄰)。
    完全消除跨節點繞路與路權衝突，平行化效率達到物理極限。
    """
    def __init__(self, cube, use_parallel: bool = True):
        super().__init__(cube)
        self.use_parallel = use_parallel

    def route(self, start_state: State) -> list[Matching]:
        state = list(start_state)
        path: list[Matching] = []
        n = self.cube.N
        dim = self.cube.dim

        for i in range(1, dim + 1):
            for j in range(i - 1, -1, -1):
                dist = 1 << j
                current_step_matching = []
                
                for u in range(n):
                    if (u & dist) == 0:
                        v = u + dist
                        dir_asc = ((u >> i) & 1) == 0
                        
                        needs_swap = False
                        if dir_asc and state[u] > state[v]:
                            needs_swap = True
                        elif not dir_asc and state[u] < state[v]:
                            needs_swap = True
                                
                        if needs_swap:
                            current_step_matching.append(self.normalize_edge(u, v))
                
                if current_step_matching:
                    for u, v in current_step_matching:
                        state[u], state[v] = state[v], state[u]
                    
                    if self.use_parallel:
                        path.append(current_step_matching)
                    else:
                        for edge in current_step_matching:
                            path.append([edge])
                    
        if not self.is_goal(tuple(state)):
            raise ValueError(f"Bitonic router failed to sort state: {state}")
            
        return path
# algorithms/base.py
from utils import Cube, Matching, State

class RoutingAlgorithm:
    def __init__(self, cube: Cube):
        self.cube = cube
        # 目的狀態通常是恆等排列 (0, 1, ..., N-1)
        self.goal_state: State = tuple(range(cube.N))

    def is_goal(self, state: State) -> bool:
        return state == self.goal_state

    def apply_move(self, state: State, move: Matching) -> State:
        """根據 Matching (一組不重複頂點的邊集合) 交換狀態中的標籤"""
        next_state = list(state)
        for u, v in move:
            next_state[u], next_state[v] = next_state[v], next_state[u]
        return tuple(next_state)

    def apply_valid_move(self, state: State, move: Matching) -> State:
        """相容 BatcherRouter 內部的調用名稱"""
        return self.apply_move(state, move)

    def normalize_edge(self, u: int, v: int) -> tuple[int, int]:
        """確保邊的方向性一致 (小索引在前)"""
        return (u, v) if u < v else (v, u)

    def route(self, start_state: State) -> list[Matching]:
        """每個子類別都必須實作此方法，回傳 Matching 的序列"""
        raise NotImplementedError
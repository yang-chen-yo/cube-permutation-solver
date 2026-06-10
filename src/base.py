from __future__ import annotations

from abc import ABC, abstractmethod

from .core import Cube, Matching, State


class RouterAlgorithm(ABC):
    NAME = "base"

    def __init__(self, cube: Cube):
        self.cube = cube
        self.goal_state = cube.identity

    @abstractmethod
    def route(self, start_state: State) -> list[Matching]:
        raise NotImplementedError

    def apply_move(self, state: State, move: Matching) -> State:
        state_list = list(state)
        for a, b in move:
            state_list[a], state_list[b] = state_list[b], state_list[a]
        return tuple(state_list)

    def apply_path(self, state: State, path: list[Matching]) -> State:
        current = state
        for move in path:
            current = self.apply_move(current, move)
        return current

    def is_goal(self, state: State) -> bool:
        return state == self.goal_state

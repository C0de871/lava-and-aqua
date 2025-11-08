from abc import ABC

from lib.models.board import Board


class Player (ABC):

    def __init__(self, position: tuple[int, int]):
        self._position = position

    def get_position(self) -> tuple[int, int]:
        return self._position

    def update_position(self, new_position: tuple[int, int]):
        self._position = new_position

    def get_available_actions(self, board: Board):
        

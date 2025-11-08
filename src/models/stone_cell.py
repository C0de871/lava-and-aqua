
from lib.models.cell_base import CellBase
from lib.models.directions_enum import Direction


class StoneCell(CellBase):
    """Stone - can be pushed by player in certain conditions"""

    def __init__(self):
        super().__init__()
        self.color = "#8B4513"
        self.display_char = "●"

    def can_player_enter(self) -> bool:
        return False

    def can_spread_through(self) -> bool:
        return False

    def on_turn_update(self):
        pass

    def can_be_pushed(self, board, from_row: int, from_col: int, direction: Direction) -> bool:
        

    def push(self, board, from_row: int, from_col: int, direction: Direction):
        """TODO: Push stone in the given direction"""
        pass

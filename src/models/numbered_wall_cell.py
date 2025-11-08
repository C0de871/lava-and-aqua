

from lib.models.cell_base import CellBase


class NumberedWallCell(CellBase):
    """Wall with a countdown number - becomes empty when reaches 0"""

    def __init__(self, number: int):
        super().__init__()
        self.number = number
        self.color = "#9B59B6"
        self.display_char = str(number)

    def can_player_enter(self) -> bool:
        return False

    def can_spread_through(self) -> bool:
        return False

    def on_turn_update(self):
        """TODO: Decrease number each turn"""
        pass

    def decrease(self):
        """TODO: Decrease the number and return True if should become empty"""
        pass

    def __repr__(self):
        return f"NumberedWall({self.number})"

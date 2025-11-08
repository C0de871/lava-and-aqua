from lib.models.cell_base import CellBase


class WaterCell(CellBase):
    """Water cell - spreads each turn"""

    def __init__(self):
        super().__init__()
        self.color = "#4444FF"
        self.display_char = "≈"

    def can_player_enter(self) -> bool:
        return False

    def can_spread_through(self) -> bool:
        return False

    def on_turn_update(self):
        """TODO: Implement water spreading logic"""
        pass

    def spread(self, board, row: int, col: int):
        """TODO: Spread water to adjacent cells"""
        pass

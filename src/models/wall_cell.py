
from lib.models.cell_base import CellBase


class WallCell(CellBase):
    """Solid wall - blocks everything"""

    def __init__(self):
        super().__init__()
        self.color = "#4A4A4A"
        self.display_char = "█"

    def can_player_enter(self) -> bool:
        return False

    def can_spread_through(self) -> bool:
        return False

    def on_turn_update(self):
        pass

    def can_stone_enter(self) -> bool:
        return False

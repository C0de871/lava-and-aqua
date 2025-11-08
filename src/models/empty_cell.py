from lib.models.cell_base import CellBase


class EmptyCell(CellBase):
    """Empty cell - player can move through"""

    def __init__(self):
        super().__init__()
        self.color = "#2B2D31"
        self.display_char = "·"

    def can_player_enter(self) -> bool:
        return True

    def can_spread_through(self) -> bool:
        return True

    def can_stone_enter(self) -> bool:
        return True

    def on_turn_update(self):
        pass

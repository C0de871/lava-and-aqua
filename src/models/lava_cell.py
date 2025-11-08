

from lib.models.cell_base import CellBase


class LavaCell(CellBase):
    """Lava cell - deadly to player, spreads each turn"""
    
    def __init__(self):
        super().__init__()
        self.color = "#FF4444"
        self.display_char = "~"
    
    def can_player_enter(self) -> bool:
        return True  # Player dies if enters
    
    def can_spread_through(self) -> bool:
        return True
    
    def on_turn_update(self):
        """TODO: Implement lava spreading logic"""
        pass
    
    def spread(self, board, row: int, col: int):
        """TODO: Spread lava to adjacent cells"""
        pass

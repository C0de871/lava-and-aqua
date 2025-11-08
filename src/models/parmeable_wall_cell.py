from lib.models.cell_base import CellBase


class PermeableWallCell(CellBase):
    """Wall that lava/water can spread through but nothing else can pass"""
    
    def __init__(self):
        super().__init__()
        self.color = "#A9A9A9"
        self.display_char = "▒"
    
    def can_player_enter(self) -> bool:
        return False
    
    def can_spread_through(self) -> bool:
        return True  # Only lava/water can spread through
    
    def on_turn_update(self):
        pass


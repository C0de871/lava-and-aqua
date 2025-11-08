
# ==================== LOGIC LAYER ====================

from abc import ABC, abstractmethod


class CellBase(ABC):
    """Base class for all cell types"""

    def __init__(self):
        self.color = "#FFFFFF"
        self.display_char = " "

    @abstractmethod
    def can_player_enter(self) -> bool:
        """Can the player move into this cell?"""
        pass

    @abstractmethod
    def can_spread_through(self) -> bool:
        """Can lava/water spread through this cell?"""
        pass

    @abstractmethod
    def can_stone_enter(self) -> bool:
        pass

    @abstractmethod
    def on_turn_update(self):
        """Called every turn to update cell state"""
        pass

    def get_color(self) -> str:
        """Get the cell's display color"""
        return self.color

    def __repr__(self):
        return self.__class__.__name__

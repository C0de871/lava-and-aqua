
from typing import Tuple
from lib.models.cell_base import CellBase


class GoalCell:
    """Goal gate - player wins when reaching this"""

    def __init__(self, position: Tuple[int, int]):
        super().__init__()
        self.color = "#00FF00"
        self.display_char = "★"
        self.position = position

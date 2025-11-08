
from typing import Tuple
from lib.models.board import Board
from lib.models.empty_cell import EmptyCell
from lib.models.goal_cell import GoalCell
from lib.models.lava_cell import LavaCell
from lib.models.numbered_wall_cell import NumberedWallCell
from lib.models.parmeable_wall_cell import PermeableWallCell
from lib.models.stone_cell import StoneCell
from lib.models.wall_cell import WallCell
from lib.models.water_cell import WaterCell


class BoardBuilder:
    """Builds and validates game boards - Pure Logic"""

    def __init__(self, rows: int, cols: int):
        self.board = Board(rows, cols)

    def place_cell(self, row: int, col: int, cell_type: str, number: int = 0):
        """Place a cell on the board"""
        cell_map = {
            "empty": EmptyCell(),
            "wall": WallCell(),
            "lava": LavaCell(),
            "water": WaterCell(),
            "stone": StoneCell(),
            "numbered_wall": NumberedWallCell(number),
            "goal": GoalCell(),
            "permeable_wall": PermeableWallCell()
        }

        if cell_type in cell_map:
            if cell_type == "goal":
                self.board.set_goal_position(row, col)
            else:
                self.board.set_cell(row, col, cell_map[cell_type])

    def set_player_start(self, row: int, col: int):
        """Set player starting position"""
        self.board.set_player_position(row, col)

    def validate_board(self) -> Tuple[bool, str]:
        """Validate that board is playable"""
        if not self.board.player_pos:
            return False, "Player starting position not set"

        if not self.board.goal_pos:
            return False, "Goal gate not set"

        return True, "Board is valid"

    def get_board(self) -> Board:
        """Get the constructed board"""
        return self.board

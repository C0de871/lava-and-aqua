
from typing import Optional, Tuple, List

from lib.models.cell_base import CellBase
from lib.models.directions_enum import Direction
from lib.models.empty_cell import EmptyCell
from lib.models.goal_cell import GoalCell


class Board:
    """Game board managing all cells and game state - Pure Logic"""

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid: List[List[CellBase]] = [[EmptyCell() for _ in range(cols)]
                                           for _ in range(rows)]
        self.goal_pos: Optional[Tuple[int, int]] = None
        self.turn_count = 0

    def set_cell(self, row: int, col: int, cell: CellBase):
        """Set a cell at the given position"""
        if self.is_valid_position(row, col):
            self.grid[row][col] = cell

    def get_cell(self, row: int, col: int) -> Optional[CellBase]:
        """Get the cell at the given position"""
        if self.is_valid_position(row, col):
            return self.grid[row][col]
        return None

    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within bounds"""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def set_player_position(self, row: int, col: int):
        """Set the player's starting position"""
        if self.is_valid_position(row, col):
            self.player_pos = (row, col)

    def set_goal_position(self, row: int, col: int):
        """Set the goal gate position"""
        if self.is_valid_position(row, col):
            self.goal_pos = (row, col)
            self.set_cell(row, col, GoalCell())

    def move_player(self, direction: Direction) -> bool:
        """
        Move player in the given direction
        TODO: Implement full movement logic:
        - Check if target cell allows entry
        - Handle stone pushing
        - Update player position
        - Return True if move succeeded
        """
        if not self.player_pos:
            return False

        if direction not in Direction:
            return False

        # TODO: Implement actual movement logic here
        return False

    def execute_turn(self, player_direction: Optional[str] = None):
        """
        Execute one complete turn
        TODO: Implement turn execution:
        1. Move player if direction given
        2. Spread all lava cells
        3. Spread all water cells
        4. Update all numbered walls
        5. Check win/lose conditions
        """
        self.turn_count += 1

        # TODO: Implement turn logic
        pass

    def check_win_condition(self) -> bool:
        """Check if player reached the goal"""
        if self.player_pos and self.goal_pos:
            return self.player_pos == self.goal_pos
        return False

    def check_lose_condition(self) -> bool:
        """
        Check if player lost (touched lava, etc.)
        TODO: Implement lose condition checking
        """
        # TODO: Implement lose condition
        return False

    def get_adjacent_positions(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get valid adjacent positions (up, down, left, right)"""
        adjacent = []
        for direction in Direction:
            dr, dc = direction.value
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                adjacent.append((new_row, new_col))
        return adjacent

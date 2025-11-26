from typing import Optional, Set
from models.direction_enum import Direction
from models.player import Player
from models.position import Position

from dataclasses import dataclass, field

from utils.zobrist_hash import Zobrist


@dataclass(init=False,)
class Board:

    row: int = field()
    col: int = field()
    grid: list[list[str]] = field()
    keys: Set[Position] = field()
    player: Player = field()
    gate_pos: Position = field()
    h: int = field()

    def __init__(self, row: int, col: int, player: Player, gate_pos: Position, grid: list[list[str]], h: int, keys: Optional[Set[Position]] = None):
        self.grid = grid
        self.row = row
        self.col = col
        if keys is None:
            keys = set()
        self.keys = keys
        self.player = player
        self.gate_pos = gate_pos
        self.h = h

    def clone(self):
        player = self.player.clone()
        gate_pos = self.gate_pos.clone()
        keys = {pos.clone() for pos in self.keys}
        grid = [row[:] for row in self.grid]
        if player:
            board = Board(self.row, self.col, player,
                          gate_pos, grid, self.h, keys)
            return board
        raise ValueError("the player is None")

    def is_valid_pos(self, pos: Position):
        return pos.x >= 0 and pos.x < self.col and pos.y >= 0 and pos.y < self.row

    def get_cell(self, pos: Position):
        if (not self.is_valid_pos(pos)):
            raise ValueError("out of bound exception")
        return self.grid[pos.y][pos.x]

    def update_cell(self, pos: Position, type: str):
        if (not self.is_valid_pos(pos)):
            raise ValueError("out of bound exception")
        if type == '.' and self.get_cell(pos) != '.':
            self.h = Zobrist.updateBoardHash(
                pos.y, pos.x,  self.get_cell(pos), self.h)
        elif type != '.' and self.get_cell(pos) == '.':
            self.h = Zobrist.updateBoardHash(
                pos.y, pos.x, type, self.h)
        elif type != '.' and self.get_cell(pos) != '.':
            self.h = Zobrist.updateBoardHash(
                pos.y, pos.x, type, self.h)
            self.h = Zobrist.updateBoardHash(
                pos.y, pos.x,  self.get_cell(pos), self.h)
        self.grid[pos.y][pos.x] = type

    def is_alive(self):
        return self.player.isAlive

    def kill(self):
        self.player.kill()

    def revive(self):
        self.player.revive()

    def is_gate_reached(self):
        return self.player.position == self.gate_pos and len(self.keys) == 0

    def is_player_touch_lava_or_wall(self):
        cell_type = self.get_cell(self.player.position)
        return cell_type == 'L' or cell_type == 'W'

    def move_player(self,  direction: Direction):
        cur_pos = self.player.position
        available_actions = self.get_available_actions()
        if (not (direction in available_actions)):
            return self
        new_player_pos = cur_pos.apply_direction(direction)
        self.h = Zobrist.updatePlayerHash(cur_pos.y, cur_pos.x, self.h)
        self.player.position = new_player_pos
        self.h = Zobrist.updatePlayerHash(
            new_player_pos.y, new_player_pos.x, self.h)
        return self

    def get_available_actions(self, old_board=None, old_direction: Direction | None = None):
        available_actions = set()
        is_stone_moved_or_was_key = False
        if old_board:
            is_stone_moved_or_was_key = self.is_stone_moved(
                old_board) or self.was_there_key(old_board)
        for direction in Direction:
            if (self.can_move_player(direction)):
                if old_direction and Direction.are_opposite(old_direction, direction) and not is_stone_moved_or_was_key:
                    continue
                if self.is_dangerous_place(direction):
                    continue
                available_actions.add(direction)
        return available_actions

    def can_move_player(self, direction: Direction):
        cur_pos = self.player.position
        new_pos = cur_pos.apply_direction(direction)
        if (not (self.is_valid_pos(new_pos))):
            return False
        cell = self.get_cell(new_pos)
        if (cell == 'L' or cell == 'A' or cell == '.'):
            return True
        if (cell == 'S'):
            can = self.can_move_stone(new_pos, direction)
            return can
        return False

    def walling(self, cur_pos: Position):
        self.update_cell(cur_pos, 'W')

    def move_stone(self, cur_stone_pos: Position, direction: Direction):
        if (not (self.can_move_stone(cur_stone_pos, direction))):

            return self
        new_stone_pose = cur_stone_pos.apply_direction(direction)
        self.update_cell(cur_stone_pos, '.')
        self.update_cell(new_stone_pose, 'S')

    def can_move_stone(self, cur_stone_pos: Position, direction: Direction):
        new_pos = cur_stone_pos.apply_direction(direction)

        if (not (self.is_valid_pos(new_pos))):
            return False
        cell = self.get_cell(new_pos)
        if (cell == 'L' or cell == 'A' or cell == '.'):

            return True
        return False

    def _get_spreadable_pos(self, cur_pos: Position):
        valid_pos = self._get_valid_neighbor(cur_pos)
        filtered_positions: Set[Position] = set()
        for pos in valid_pos:
            cell = self.get_cell(pos)
            if cell == '.' or cell == 'P':
                filtered_positions.add(pos)
        return filtered_positions

    def is_lava_near_aqua(self, cur_pos: Position):
        for direction in Direction:
            new_pos = cur_pos.apply_direction(direction)
            if not self.is_valid_pos(new_pos):
                continue
            cell = self.get_cell(new_pos)
            if cell.startswith('A'):
                return True
        return False

    def _get_valid_neighbor(self, cur_pos: Position):
        positions: Set[Position] = set()
        for direction in Direction:
            pos = cur_pos.apply_direction(direction)
            if not self.is_valid_pos(pos):
                continue
            positions.add(pos)
        return positions

    def _update_key(self):
        self.keys.remove(self.player.position)
        self.h = Zobrist.updateKeysHash(self.player.position.y,
                                        self.player.position.x, self.h)

    def get_wall_counter(self, cell: str):
        str_num = cell[1:]
        num = int(str_num)
        num -= 1
        if num <= 0:
            return '.'
        new_str_num = str(num)
        new_cell = 'C'+new_str_num
        return new_cell

    def is_stone_moved(self, old_board):
        new_player_pos = self.player.position
        cell = old_board.get_cell(new_player_pos)
        if cell == 'S':
            return True
        else:
            return False

    def was_there_key(self, old_board):
        new_player_pos = self.player.position
        return new_player_pos in old_board.keys

    def is_dangerous_place(self, direction):
        new_pos = self.player.position.apply_direction(direction)
        if self.get_cell(new_pos) == 'L':
            return True

        for new_direction in Direction:
            if self.get_cell(new_pos) == 'S':
                if new_direction == direction:
                    continue
            neighbor_pos = new_pos.apply_direction(new_direction)
            neighbor_cell = self.get_cell(neighbor_pos)
            if (neighbor_cell == 'L' or neighbor_cell == 'LP'):
                return True
        return False

    def transition_model(self, direction: Direction):

        new_board = self.clone()

        new_pos_dic: dict[Position, str] = {}

        if (not (new_board.can_move_player(direction))):
            return new_board
        new_board.move_player(direction)

        cell_in_direction = new_board.get_cell(new_board.player.position)
        if (cell_in_direction == 'S'):
            new_board.move_stone(
                new_board.player.position, direction)

        # check if there is a key in the new player position
        if (new_board.player.position in new_board.keys):
            new_board._update_key()
            # get new lava and aqua positions:
        for y, row in enumerate(new_board.grid):
            for x, cell in enumerate(row):
                pos = Position(x, y)
                if cell.startswith('L'):
                    if new_board.is_lava_near_aqua(pos):
                        new_board.walling(pos)
                        continue
                    new_positions = new_board._get_spreadable_pos(pos)
                    for spread_pos in new_positions:
                        if new_pos_dic.get(spread_pos) == 'A':
                            new_board.walling(spread_pos)
                            new_pos_dic.pop(spread_pos, None)
                            continue
                        if new_board.get_cell(spread_pos) == 'P':
                            new_pos_dic[spread_pos] = 'LP'
                            continue
                        new_pos_dic[spread_pos] = 'L'

                elif cell.startswith('A'):
                    new_positions = new_board._get_spreadable_pos(pos)
                    for spread_pos in new_positions:
                        if new_pos_dic.get(spread_pos) == 'L':
                            new_board.walling(spread_pos)
                            new_pos_dic.pop(spread_pos, None)
                            continue
                        if new_board.get_cell(spread_pos) == 'P':
                            new_pos_dic[spread_pos] = 'AP'
                            continue
                        new_pos_dic[spread_pos] = 'A'
                elif cell[0] == 'C':
                    new_pos_dic[pos] = new_board.get_wall_counter(cell)

        for key, value in new_pos_dic.items():

            new_board.update_cell(key, value)

        if new_board.is_player_touch_lava_or_wall():
            new_board.kill()

        return new_board

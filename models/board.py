from typing import Optional, Set
from models.aqua import Aqua
from models.cell import Cell
from models.count_down_wall import CountDownWall
from models.direction_enum import Direction
from models.empty import Empty
from models.entity import Entity
from models.ground import Ground
from models.lava import Lava
from models.player import Player
from models.position import Position
from models.solid_wall import SolidWall
from models.stone import Stone
from models.wall import Wall

from dataclasses import dataclass, field


@dataclass(init=False,)
class Board:

    row: int = field()
    col: int = field()
    grid: list[list[Cell]] = field()
    keys: Set[Position] = field()
    player:Player = field()
    gate_pos: Position = field()

    def __init__(self, row: int, col: int, player_pos: Position, player: Player, gate_pos: Position, grid: list[list[Cell]], keys: Optional[Set[Position]] = None):
        self.grid = grid
        self.row = row
        self.col = col
        if keys is None:
            keys = set()
        self.keys = keys
        player.position = player_pos
        self.player = player
        self.gate_pos = gate_pos

    def is_valid_pos(self, pos: Position):
        return pos.x >= 0 and pos.x < self.col and pos.y >= 0 and pos.y < self.row

    def get_cell_atpos(self, pos: Position):
        if (not self.is_valid_pos(pos)):
            print(f' x is {pos.x}')
            print(f' y is {pos.y}')
            raise ValueError("out of bound exception")
        return self.grid[pos.y][pos.x]

    def set_entity_atpos(self, pos: Position, entity: Entity | None):
        if (not self.is_valid_pos(pos)):
            raise ValueError("out of bound exception")
        self.grid[pos.y][pos.x].entity = entity

    def set_ground_atpos(self, pos: Position, ground: Ground):
        if (not self.is_valid_pos(pos)):
            raise ValueError("out of bound exception")
        self.grid[pos.y][pos.x].ground = ground

    def is_player_alive(self):
        return self.player.isAlive

    def kill_player(self):
        self.player.kill()

    def revive_player(self):
        self.player.revive()

    def is_gate_reached(self):
        return self.player.position == self.gate_pos and len(self.keys) == 0

    def is_player_touch_lava_or_wall(self):
        return isinstance(self.get_cell_atpos(self.player.position).ground, Lava) or isinstance(self.get_cell_atpos(self.player.position).entity, Wall)

    def move_player(self, cur_pos: Position, direction: Direction):
        available_actions = self.get_available_actions(cur_pos)
        if (not (direction in available_actions)):
            return self
        print("can move player")
        new_player_pose = cur_pos.apply_direction(direction)
        self.player.position = new_player_pose
        return self

    def get_available_actions(self, cur_pos: Position):
        available_actions = set()
        for direction in Direction:
            if (self.can_move_player(cur_pos, direction)):
                available_actions.add(direction)
        return available_actions

    def can_move_player(self, cur_pos: Position, direction: Direction):
        new_pos = cur_pos.apply_direction(direction)
        if (not (self.is_valid_pos(new_pos))):
            return False
        cell = self.get_cell_atpos(new_pos)
        if (cell.is_wall()):
            return False
        if (cell.is_stone()):
            can = self.can_move_stone(new_pos, direction)
            return can
        return True

    def walling(self, cur_pos: Position):
        self.set_ground_atpos(cur_pos, Empty())
        self.set_entity_atpos(cur_pos, SolidWall(is_permeable=False))

    def move_stone(self, cur_stone_pos: Position, direction: Direction):
        if (not (self.can_move_stone(cur_stone_pos, direction))):
            print("can't push the stone")
            return self
        new_stone_pose = cur_stone_pos.apply_direction(direction)
        self.set_entity_atpos(cur_stone_pos, None)
        self.set_ground_atpos(cur_stone_pos, Empty())

        self.set_entity_atpos(new_stone_pose, Stone())
        self.set_ground_atpos(new_stone_pose, Empty())

    def can_move_stone(self, cur_stone_pos: Position, direction: Direction):
        new_pos = cur_stone_pos.apply_direction(direction)
        print("check if we can push the stone")
        if (not (self.is_valid_pos(new_pos))):
            return False
        cell = self.get_cell_atpos(new_pos)
        if (cell.is_wall() or cell.is_stone()):
            print("the cell is wall or stone")
            return False
        return True

    def _get_spreadable_pos(self, cur_pos: Position):
        valid_pos = self._get_valid_neighbor(cur_pos)
        filtered_positions: Set[Position] = set()
        for pos in valid_pos:
            cell = self.get_cell_atpos(pos)
            if cell.can_liquid_pass():
                print("liquid can pass")
                filtered_positions.add(pos)
        return filtered_positions

    def is_lava_near_aqua(self, cur_pos: Position):
        for direction in Direction:
            new_pos = cur_pos.apply_direction(direction)
            if not self.is_valid_pos(new_pos):
                continue
            cell = self.get_cell_atpos(new_pos)
            if isinstance(cell.ground, Aqua):
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

    def update(self, direction: Direction):

        new_pos_dic: dict[Position, Ground] = {}
        counter_positions = []

        # check if we can push the stone first and push it if we can
        new_pos = self.player.position.apply_direction(direction)
        if (not self.is_valid_pos(new_pos)):
            new_pos = self.player.position
        cell_in_direction = self.get_cell_atpos(new_pos)
        if (isinstance(cell_in_direction.entity, Stone)):
            self.move_stone(
                new_pos, direction)

        # check if the player can move if not don't continue and stop update function else move the player
        if (not (self.can_move_player(self.player.position, direction))):
            return
        self.move_player(self.player.position, direction)

        # check if there is a key in the new player position
        if (self.player.position in self.keys):
            self.keys.remove(self.player.position)

        # get new lava and aqua positions:
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                pos = Position(x, y)
                if isinstance(cell.ground, Lava):
                    if self.is_lava_near_aqua(pos):
                        self.walling(pos)
                        continue
                    new_positions = self._get_spreadable_pos(pos)
                    for spread_pos in new_positions:
                        if isinstance(new_pos_dic.get(spread_pos), Aqua):
                            self.walling(spread_pos)
                            new_pos_dic.pop(spread_pos, None)
                            continue
                        new_pos_dic[spread_pos] = Lava()

                elif isinstance(cell.ground, Aqua):  # type: ignore
                    new_positions = self._get_spreadable_pos(pos)
                    for spread_pos in new_positions:
                        if isinstance(new_pos_dic.get(spread_pos), Lava):
                            self.walling(spread_pos)
                            new_pos_dic.pop(spread_pos, None)
                            continue
                        new_pos_dic[spread_pos] = Aqua()
                elif isinstance(cell.entity, CountDownWall):
                    counter_positions.append(pos)

        for key, value in new_pos_dic.items():
            print(key.__str__, value.__str__)
            self.set_ground_atpos(key, value)
        for pos in counter_positions:
            cell = self.get_cell_atpos(pos)
            cell.update_count_down_wall()

        if self.is_player_touch_lava_or_wall():
            self.kill_player()
            return

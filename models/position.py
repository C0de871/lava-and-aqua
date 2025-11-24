from dataclasses import dataclass, field
from models.direction_enum import Direction


@dataclass(init=False)
class Position:

    __x: int = field()
    __y: int = field()
    def __init__(self, x: int, y: int):
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = value

    def apply_direction(self, direction: Direction):
        dx, dy = direction.value
        return Position(self.x + dx, self.y+dy)

    def __eq__(self, other):
        return isinstance(other, Position) and self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"Position({self.x}, {self.y})"
